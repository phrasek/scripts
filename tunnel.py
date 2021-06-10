from subprocess import Popen
import argparse
import signal
from time import sleep

parser = argparse.ArgumentParser(description="Create an ssh tunnel and keep it alive.")
parser.add_argument("sshpath", type=str, help="Path of ssh executable")
parser.add_argument("host", type=str, help="Remote host as in ~/.ssh/config")
parser.add_argument("localport", type=int, help="Local port for tunnel")
parser.add_argument(
    "-remoteport",
    type=int,
    help="Remote port for tunnel. Required when using type other than dynamic",
)
parser.add_argument(
    "-type",
    type=str,
    help="Forward type. Defaults to dynamic. Valid values are: [D,R,L]",
)

__all__ = ["Tunnel"]


class Tunnel:
    def __init__(
        self,
        localport: int,
        host: str,
        sshpath: str,
        remoteport: int = None,
        ftype: str = "D",
    ) -> None:
        self.localport = localport
        self.remoteport = remoteport
        self.host = host
        self.sshpath = sshpath
        type = "-" + ftype if ftype is not None else "-D"
        if type == "-D":
            self.command = [
                sshpath,
                type,
                str(self.localport),
                "-f",
                "-q",
                "-N",
                host,
            ]
        elif remoteport is not None:
            if type in ["-R", "-L"]:
                self.command = [
                    sshpath,
                    type,
                    f"{str(self.remoteport)}:localhost:{str(self.localport)}",
                    "-f",
                    "-q",
                    "-N",
                    host,
                ]
            else:
                raise ValueError(
                    f"Invalid forward type: {type[1:]}. Valid values are: [D,R,L]."
                )
        else:
            raise ValueError("Remote port required when using non dynamic forwarding.")
        self.__running = True

    def start(self):
        self.tunnel = Popen(self.command, shell=False, creationflags=0x08000000)
        while True:
            self.tunnel.wait()
            if self.tunnel.poll() and self.__running:
                self.tunnel = Popen(self.command, shell=False, creationflags=0x08000000)
                sleep(30)

    def stop(self):
        self.__running = False
        self.tunnel.terminate()


def main() -> None:
    args = vars(parser.parse_args())
    t = Tunnel(
        localport=args["localport"],
        host=args["host"],
        sshpath=args["sshpath"],
        ftype=args["type"],
        remoteport=args["remoteport"],
    )
    t.start()

    def keyboardInterruptHandler(signal, frame):
        t.stop()

    signal.signal(signal.SIGINT, keyboardInterruptHandler)


if __name__ == "__main__":
    main()
