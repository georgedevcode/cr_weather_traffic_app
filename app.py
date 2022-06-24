import re
import os
import asyncio
import aiohttp
import json
import requests
from aioflask import Flask, render_template, make_response
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient


def GetOpenWeatherSecretKey():
    credential = DefaultAzureCredential()
    key_client = SecretClient(vault_url="https://crweatherappkeys.vault.azure.net/", credential=credential)
    key = key_client.get_secret("openweatherkey")
    print(f"Secret: {key.value}")
    return key.value

"""
--------------------------------------------
Globals: Empty arrays to hold and manipulate
weather data
--------------------------------------------
"""
weather_data = []
curr_weather_conditions = []

async def ExtractWeatherData(*locations, api_key):
    """
    Extracing the weather data based on the locations
    """
    ExtractedWeatherData = False
    if len(locations) <= 7:
        async with aiohttp.ClientSession() as session:
            for location in locations:
                async with session.get("http://api.openweathermap.org/data/2.5/weather?appid={api_key}&q={location},CR&units=metric" .format(api_key, location)) as response:
                    if response.status == 200:
                        app.logger.info(f"HTTP GET request: {response.status}")
                        data = await response.json()
                        weather_data.append(data)
                        ExtractedWeatherData = True
                    else:
                        app.logger.error(f"Couldn't get weather data, HTTP code: {response.status}")
    return ExtractedWeatherData

async def TransformData(weather_data):
    """
    Transforming the data to something more easy to handle instead of JSON format.
    And getting the weather conditions we are only interested in
    """
    DataTransformed = False
    if len(weather_data) <= 7:
        for d in weather_data:
            conditions = d["main"].copy()
            conditions.update({"condition":d["weather"][0], "location":d["name"]})
            curr_weather_conditions.append(conditions)
            DataTransformed = True
    else:
        app.logger.error("Data size is not the expected")
    return DataTransformed

async def LoadDisplayTransformedData(curr_weather_conditions):
    if not curr_weather_conditions:
        app.logger.warning("The curr_weather_conditions list is empty")
        r = await InternalError(500)
    else:
        app.logger.info("Data is about to be rendered in the front page")
        r = await render_template("index.html", conditions=curr_weather_conditions)
    return r

app = Flask(__name__)

@app.route("/")
async def main_page():

    api_key = GetOpenWeatherSecretKey()
    if api_key != None:
        app.logger.debug("Sucess:Retrieved Open Weather API key from Azure Vault")
    else:
        InternalError(500)
        
    if await ExtractWeatherData("Heredia", "San Jose", "Alajuela", "Cartago", "Guanacaste", "Limon", "Puntarenas", api_key):
        app.logger.debug("Sucess:Retrieved weather data")
    else:
        app.logger.debug("Failed:Retrieved weather data")

    if await TransformData(weather_data):
        app.logger.debug("Sucess: Transformed data")
    else:
        app.logger.debug("Failed: Transformed data")

    render = await LoadDisplayTransformedData(curr_weather_conditions)
    if render:
        app.logger.debug("Sucess: Rendered data")
    else:
        app.logger.debug("Failed: Rendered data")

    return render

@app.errorhandler(500)
async def InternalError(error):
    resp = make_response(await render_template("500_error.html", error=error))
    resp.headers["Content-Type"] = "text/html"
    return resp

if __name__ == '__main__':
    app.run()