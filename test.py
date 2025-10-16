import paho.mqtt.client as mqtt
import time

# MQTT broker info
broker = "192.168.190.91"  # IP của máy A
port = 1883
topic = "test/topic"

# Callback khi kết nối
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("✅ Đã kết nối với MQTT Broker!")
        client.subscribe(topic)
        print(f"📡 Đang lắng nghe trên topic: {topic}")
    else:
        print(f"❌ Kết nối thất bại, mã lỗi: {rc}")

# Callback khi nhận tin nhắn
def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8').strip()
    print(f"📩 Nhận: {payload} từ topic {msg.topic}")

# Tạo client MQTT
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="Subscriber")
client.on_connect = on_connect
client.on_message = on_message

# Kết nối với retry
max_retries = 5
for i in range(max_retries):
    try:
        client.connect(broker, port, keepalive=60)
        break
    except Exception as e:
        print(f"❌ Lỗi kết nối (lần {i+1}/{max_retries}): {e}")
        if i == max_retries - 1:
            print("❌ Không thể kết nối. Thoát...")
            exit(1)
        time.sleep(5)

# Bắt đầu vòng lặp MQTT
try:
    client.loop_forever()
except KeyboardInterrupt:
    print("\n👋 Dừng nhận")
    client.disconnect()