import requests
from dotenv import load_dotenv, find_dotenv
import os
from datetime import datetime, timedelta

load_dotenv(find_dotenv())


async def get_weather_today(city):
	"""
         Погода на сегодня
    """
	url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={os.getenv("OPENWEATHERMAP_API_KEY")}&units=metric&lang=ru'
	response = requests.get(url, timeout=10)
	data = response.json()

	if response.status_code == 200:
		today = datetime.now()
		weather_description = data['weather'][0]['description']
		temperature = data['main']['temp']
		feels_like = data['main']['feels_like']
		humidity = data['main']['humidity']
		wind_speed = data['wind']['speed']

		weather_report = (
			f"Погода в городе {city} на {today.strftime('%d.%m.%Y')}:\n"
			f"Описание: {weather_description}\n"
			f"Температура: {temperature}°C\n"
			f"Ощущается как: {feels_like}°C\n"
			f"Влажность: {humidity}%\n"
			f"Скорость ветра: {wind_speed} м/с"
		)
	else:
		return None

	return weather_report


async def get_weather_tomorrow(city):
	"""
        Погода на завтра
    """
	url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={os.getenv("OPENWEATHERMAP_API_KEY")}&units=metric&lang=ru'
	response = requests.get(url)
	data = response.json()

	if response.status_code == 200:
		tomorrow = datetime.now() + timedelta(days=1)
		tomorrow_noon = tomorrow.replace(hour=12, minute=0, second=0, microsecond=0)

		# Найдем ближайшую запись к завтрашнему полудню
		closest_forecast = min(data['list'], key=lambda x: abs(tomorrow_noon - datetime.fromtimestamp(x['dt'])))

		weather_description = closest_forecast['weather'][0]['description']
		temperature = closest_forecast['main']['temp']
		feels_like = closest_forecast['main']['feels_like']
		humidity = closest_forecast['main']['humidity']
		wind_speed = closest_forecast['wind']['speed']

		weather_report = (
			f"Погода в городе {city} на {tomorrow.strftime('%d.%m.%Y')}:\n"
			f"Описание: {weather_description}\n"
			f"Температура: {temperature}°C\n"
			f"Ощущается как: {feels_like}°C\n"
			f"Влажность: {humidity}%\n"
			f"Скорость ветра: {wind_speed} м/с"
		)
	else:
		weather_report = "Город не найден. Пожалуйста, проверьте название и попробуйте снова."

	return weather_report


async def get_weather_for_x_days(city, x):
	url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={os.getenv("OPENWEATHERMAP_API_KEY")}&units=metric&lang=ru'
	response = requests.get(url)
	data = response.json()

	if response.status_code == 200:
		today = datetime.now()
		forecasts = []

		for i in range(0, x):
			target_date = today + timedelta(days=i)
			target_noon = target_date.replace(hour=12, minute=0, second=0, microsecond=0)

			# Найдем ближайшую запись к полудню target_date
			closest_forecast = min(data['list'], key=lambda x: abs(target_noon - datetime.fromtimestamp(x['dt'])))

			weather_description = closest_forecast['weather'][0]['description']
			temperature = closest_forecast['main']['temp']
			feels_like = closest_forecast['main']['feels_like']
			humidity = closest_forecast['main']['humidity']
			wind_speed = closest_forecast['wind']['speed']

			forecasts.append(
				f"Погода в городе {city} на {target_date.strftime('%d.%m.%Y')}:\n"
				f"Описание: {weather_description}\n"
				f"Температура: {temperature}°C\n"
				f"Ощущается как: {feels_like}°C\n"
				f"Влажность: {humidity}%\n"
				f"Скорость ветра: {wind_speed} м/с\n"
			)

		weather_report = "\n".join(forecasts)
	else:
		weather_report = "Город не найден. Пожалуйста, проверьте название и попробуйте снова."

	return weather_report
