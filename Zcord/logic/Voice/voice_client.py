import asyncio
import json
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer
from aiortc.contrib.media import MediaPlayer, MediaRecorder


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
                # Запускаем воспроизведение через MediaRecorder
                self.recorder = MediaRecorder("out.wav", format="wav")
                self.recorder.addTrack(track)
                asyncio.create_task(self.recorder.start())

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

                player = MediaPlayer("audio=Микрофон (USB PnP Audio Device)", format="dshow", options={
                    "channels": "1", "sample_rate": "48000"
                })
                self.pc.addTrack(player.audio)

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

                player = MediaPlayer("audio=Микрофон (USB PnP Audio Device)", format="dshow", options={
                    "channels": "1", "sample_rate": "48000"
                })  # Windows
                self.pc.addTrack(player.audio)

                answer = await self.pc.createAnswer()
                await self.pc.setLocalDescription(answer)

                self.writer.write(json.dumps({
                    "type": "answer",
                    "sdp": self.pc.localDescription.sdp,
                    "room_id": self.room_id
                }).encode())
                await self.writer.drain()

            elif message["type"] == "answer":
                print("Получен answer, устанавливаем...")
                await self.pc.setRemoteDescription(
                    RTCSessionDescription(sdp=message["sdp"], type="answer")
                )

            elif message["type"] == "candidate":
                print("Получен ICE candidate...")
                await self.pc.addIceCandidate(message["candidate"])


async def main():
    client = VoiceClient()
    await client.start()
    await asyncio.Event().wait()

asyncio.run(main())
