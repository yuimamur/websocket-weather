import json
import time
import random
import requests
import tornado.websocket
import tornado.web
import tornado.ioloop

# OpenWeatherMap API設定
API_KEY = "API Key"  # ← 自分のAPIキーに置き換えてください
CITY_NAME = "Tokyo"
URL_TEMPLATE = "http://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=metric&lang=ja"

def get_weather_data(city=CITY_NAME):
    try:
        url = URL_TEMPLATE.format(city, API_KEY)
        response = requests.get(url)
        weather = response.json()
        temp = weather["main"]["temp"]
        humidity = weather["main"]["humidity"]
        wind_speed = weather["wind"]["speed"]
        icon = weather["weather"][0]["icon"]
        return temp, humidity, wind_speed, icon
    except Exception as e:
        print(f"Error: {e}")
        return 0, 0, 0, "01d"  # fallback値

class SendWebSocket(tornado.websocket.WebSocketHandler):
    def open(self):
        print("Session Opened. IP:", self.request.remote_ip)
        self.ioloop = tornado.ioloop.IOLoop.current()
        self.running = True
        self.city = CITY_NAME  # 初期都市
        self.send_websocket()

    def on_message(self, message):
        try:
            data = json.loads(message)
            if "city" in data:
                self.city = data["city"]
                print(f"都市が変更されました: {self.city}")
        except Exception as e:
            print("受信エラー:", e)

    def on_close(self):
        print("Session Closed")
        self.running = False

    def check_origin(self, origin):
        return True

    def send_websocket(self):
        if not self.running:
            return

        self.ioloop.add_timeout(time.time() + 1, self.send_websocket)
        temp, humidity, wind_speed, icon = get_weather_data(self.city)
        message = json.dumps({
            "temp": temp,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "icon": icon
        })
        try:
            self.write_message(message)
        except Exception as e:
            print("送信エラー:", e)

app = tornado.web.Application([
    (r"/ws/display", SendWebSocket),
])

if __name__ == "__main__":
    print("Starting server on http://localhost:8282")
    app.listen(8282)
    tornado.ioloop.IOLoop.current().start()

