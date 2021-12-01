import os
import atexit
from serial import Serial, serialutil
from mido import Message

class TerminalColors:
  BLUE = '\033[94m'
  CYAN = '\033[96m'
  GREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  END = '\033[0m'
  BOLD = '\033[1m'
  ITALIC = '\033[3m'
  UNDERLINE = '\033[4m'

def exit_handler():
  print(TerminalColors.END, end='')

atexit.register(exit_handler)

def print_help():
  separator_line = f"+{'-' * (34 + len(port_name) + len(baudrate))}+"

  print(f'''{separator_line}
| Connected to {TerminalColors.GREEN}`{port_name}`{TerminalColors.END} with baudrate {TerminalColors.GREEN}`{baudrate}`{TerminalColors.END} |
{separator_line}

syntax:
  [command] [note] [velocity] [channel]

  {TerminalColors.ITALIC}command{TerminalColors.END}
    Optional. Defaults to `note_on`. Possible values:
      * `note_on` - send a `NOTE ON` MIDI message
      * `note_off` - send a `NOTE OFF` MIDI message
      * `exit` - exit the programme
      * `:q` - exit the programme
  {TerminalColors.ITALIC}note{TerminalColors.END}
    Optional. Integer (0..127). Defaults to `60` (C4 note)
  {TerminalColors.ITALIC}velocity{TerminalColors.END}
    Optional. Integer (0..127). Defaults to `64` (Mezzo forte)
  {TerminalColors.ITALIC}channel{TerminalColors.END}
    Optional. Integer (0..15). Defaults to `0` (channel 1)

  Optional parameters may be set to `.` to retain their default value.''')

def build_message(command):
  command = command.split()
  # breakpoint()
  msg_type = command[0] if len(command) > 0 and command[0] != '.' else 'note_on'
  note = int(command[1]) if len(command) > 1 and command[1] != '.' else 60
  velocity = int(command[2]) if len(command) > 2 and command[2] != '.' else 64
  channel = int(command[3]) if len(command) > 3 and command[3] != '.' else 0

  if msg_type not in {'', 'note_on', 'note_off'} or note not in range(0, 127) or velocity not in range(0, 127) or channel not in range(0, 16):
    print('No such command!\n')
    return

  return Message(msg_type, note=note, velocity=velocity, channel=channel)

port_name = os.getenv('PORT_NAME') or '/dev/tty.usbmodem103'
baudrate = os.getenv('BAUDRATE') or '115200'
ser = None
try:
  ser = Serial(port_name, baudrate)
except serialutil.SerialException:
  print(f'No such port: {TerminalColors.FAIL}`{port_name}`{TerminalColors.END}')
  exit()

print_help()
print()

while True:
  print(end=TerminalColors.END)
  print(f'cmd$ ', end=TerminalColors.CYAN)

  command = input().strip().lower()
  print(end=TerminalColors.END)

  if command in {':q', 'exit'}:
    exit()

  msg = build_message(command)

  if not msg:
    continue

  msg_bytes = bytes(msg.bytes())
  msg_hex = ''.join('0x{:02x} '.format(x) for x in msg_bytes).strip()
  print(f'message:  {TerminalColors.GREEN}{msg}{TerminalColors.END}')
  print(f'ascii:    {TerminalColors.GREEN}{msg_bytes}{TerminalColors.END}')
  print(f'hex:      {TerminalColors.GREEN}{msg_hex}{TerminalColors.END}')
  ser.write(msg_bytes)
  print()
