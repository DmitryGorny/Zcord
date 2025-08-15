import asyncio
import json

import pyaudio
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer, MediaStreamTrack
from aiortc.contrib.media import MediaPlayer, MediaRecorder


class SilenceStreamTrack(MediaStreamTrack):
    kind = "audio"

    def __init__(self):
        super().__init__()  # инициализация базового трека
        self.sample_rate = 48000
        self.samples_per_frame = int(self.sample_rate / 100)  # 10мс на фрейм

    async def recv(self):
        # timestamp и pts для корректной синхронизации
        pts, time_base = await self.next_timestamp()

        # пустой аудиофрейм
        frame = av.AudioFrame(format="s16", layout="mono", samples=self.samples_per_frame)
        for plane in frame.planes:
            plane.update(b"\x00" * plane.buffer_size)

        frame.pts = pts
        frame.sample_rate = self.sample_rate
        frame.time_base = time_base
        return frame


class VoiceClient:
    def __init__(self):
        self.pc = RTCPeerConnection(configuration=RTCConfiguration(
            iceServers=[RTCIceServer(urls=['stun:stun.l.google.com:19302'])]
        ))
        self.writer = None
        self.room_id = "default_room"

        @self.pc.on("track")
        def on_track(track):
            if track.kind == "audio":
                print("Аудио получено!")

                async def play_audio(track):
                    p = pyaudio.PyAudio()
                    stream = p.open(format=pyaudio.paInt16,  # 16-бит PCM
                                    channels=2,  # моно, если надо стерео — поставь 2
                                    rate=48000,  # WebRTC обычно 48 kHz
                                    output=True)

                    try:
                        while True:
                            frame = await track.recv()
                            pcm = frame.to_ndarray()

                            # Если стерео нужно:
                            # if pcm.ndim == 1:
                            #     pcm = np.stack([pcm, pcm], axis=-1)

                            # Преобразуем в bytes
                            stream.write(pcm.tobytes())
                    finally:
                        stream.stop_stream()
                        stream.close()
                        p.terminate()
                # Запускаем воспроизведение через MediaRecorder
                asyncio.create_task(play_audio(track))

        @self.pc.on("icecandidate")
        def on_ice_candidate(candidate):
            if candidate and self.writer:
                self.writer.write(json.dumps({
                    "type": "candidate",
                    "candidate": {
                        "candidate": candidate.candidate,
                        "sdpMid": candidate.sdpMid,
                        "sdpMLineIndex": candidate.sdpMLineIndex
                    },
                    "room_id": self.room_id
                }).encode())
                asyncio.ensure_future(self.writer.drain())

        @self.pc.on("iceconnectionstatechange")
        def on_ice_change():
            print(f"ICE состояние: {self.pc.iceConnectionState}")

        @self.pc.on("connectionstatechange")
        def on_conn_change():
            print(f"Cостояние: {self.pc.connectionState}")

    async def start(self):
        # Подключаемся к серверу
        self.reader, self.writer = await asyncio.open_connection("localhost", 55559)

        # Отправляем запрос на вход в комнату
        self.writer.write(json.dumps({
            "type": "join",
            "room_id": self.room_id
        }).encode())
        await self.writer.drain()

        while True:
            data = await self.reader.read(4096)
            if not data:
                break

            message = json.loads(data.decode())
            print("Получено:", message)

            if message["type"] == "wait_peer":
                print("Создаю оффер для P2P соединения...")
                # Захват аудио с микрофона

                silence_track = SilenceStreamTrack()
                self.audio_sender = self.pc.addTrack(silence_track)
                offer = await self.pc.createOffer()
                await self.pc.setLocalDescription(offer)

                self.writer.write(json.dumps({
                    "type": "offer",
                    "sdp": self.pc.localDescription.sdp,
                    "room_id": self.room_id
                }).encode())
                await self.writer.drain()

            elif message["type"] == "offer":
                print("Получен оффер, отправляем ответ...")
                await self.pc.setRemoteDescription(
                    RTCSessionDescription(sdp=message["sdp"], type="offer")
                )

                silence_track = SilenceStreamTrack()
                self.audio_sender = self.pc.addTrack(silence_track)
                answer = await self.pc.createAnswer()
                await self.pc.setLocalDescription(answer)

                self.writer.write(json.dumps({
                    "type": "answer",
                    "sdp": self.pc.localDescription.sdp,
                    "room_id": self.room_id
                }).encode())
                await self.writer.drain()

                # Готовы к старту (второй клиент)
                self.writer.write(json.dumps({
                    "type": "ready_for_voice",
                    "room_id": self.room_id
                }).encode())
                await self.writer.drain()

            elif message["type"] == "answer":
                print("Получен answer, устанавливаем...")
                await self.pc.setRemoteDescription(
                    RTCSessionDescription(sdp=message["sdp"], type="answer")
                )
                # Готовы к старту (первый клиент)
                self.writer.write(json.dumps({
                    "type": "ready_for_voice",
                    "room_id": self.room_id
                }).encode())
                await self.writer.drain()

            elif message["type"] == "candidate":
                print("Получен ICE candidate...")
                await self.pc.addIceCandidate(message["candidate"])

            elif message["type"] == "start_voice":
                print("Старт войса")
                mic = MediaPlayer(
                    "audio=Микрофон (USB PnP Audio Device)",
                    format="dshow",
                    options={"channels": "1", "sample_rate": "48000"}
                )
                self.audio_sender.replaceTrack(mic.audio)

async def main():
    client = VoiceClient()
    await client.start()
    await asyncio.Event().wait()

asyncio.run(main())
