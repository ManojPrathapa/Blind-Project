
from speech_to_text import listen_command

print("🎧 Say something into your mic...")
command = listen_command()
print("✅ You said:", command)
