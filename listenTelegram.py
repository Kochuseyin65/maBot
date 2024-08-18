from telethon import TelegramClient, events
import telegram.ext
import telegram

import okx.Trade as Trade
import okx.MarketData as MarketData
import okx.Account as Account
import okx.MarketData as MarketData
import okx.PublicData as PublicData
import time


api_key = 'f1fa9974-3e01-4e45-96f1-29390dea9872'
secret_key = 'E982D22FF4E82880FD9DFDE29D99ED74'
passphrase = '2006Hsyn..'

leverage = "10"

position = {"coin": "", "side": ""}

flag = "0"  # live trading: 0, demo trading: 1

marketDataAPI = MarketData.MarketAPI(flag=flag)
accountAPI = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)
tradeAPI = Trade.TradeAPI(api_key, secret_key, passphrase, False, flag="0")

result = accountAPI.set_position_mode(
    posMode="long_short_mode"
)

ticker = marketDataAPI.get_ticker(
    instId="XRP-USDT-SWAP"
)


    

def get_adjusted_contract_size(usdt_amount, coin_pair, precision):
    # Enstrüman detaylarını al
    instrument_details = accountAPI.get_instruments(instType="SWAP", instId=f"{coin_pair}-USDT-SWAP")
    
    if not instrument_details:
        raise ValueError(f'Enstrüman bulunamadı: {coin_pair}-USDT-SWAP')
    
    # Lot büyüklüğünü ve sözleşme değerini al

    print(instrument_details)
    lot_size = float(instrument_details["data"][0]['lotSz'])  # Lot büyüklüğü
    contract_value = float(instrument_details["data"][0]['ctVal'])  # Sözleşme değeri
    
    # Piyasa fiyatını al
    ticker = marketDataAPI.get_ticker(f'{coin_pair}-USDT-SWAP')
    price = float(ticker["data"][0]['last'])

    # Dolar cinsinden sözleşme değeri
    dollar_value_per_contract = contract_value * price

    # Kaç sözleşme gerektiğini hesaplayın
    contract_size = usdt_amount / dollar_value_per_contract
    print(lot_size)

    # Lot büyüklüğüne göre sözleşme miktarını ayarlayın
    adjusted_contract_size = max(round(contract_size / lot_size) * lot_size, lot_size)

    adjusted_contract_size = round(adjusted_contract_size, precision)

    print(f'Ayarlanmış Sözleşme Miktarı: {adjusted_contract_size}')

    return adjusted_contract_size

# Örnek kullanım
# adjusted_contract_size = get_adjusted_contract_size(120, 'XRP', 6)
# print(f'Ayarlanmış Sözleşme Miktarı: {adjusted_contract_size}')

# def usdt_to_contract_and_place_order(usdt_amount, coin_pair):
#     # Enstrüman detaylarını al
#     instrument_details = accountAPI.get_instruments(instType= "SWAP", instId = "XRP-USDT-SWAP")
    
#     if not instrument_details:
#         raise ValueError(f'Enstrüman bulunamadı: {coin_pair}-USDT-SWAP')
    
#     # Lot büyüklüğünü ve sözleşme değerini al
#     print(instrument_details)
#     lot_size = float(instrument_details["data"][0]['lotSz'])  # Lot büyüklüğü
#     contract_value = float(instrument_details["data"][0]['ctVal'])  # Sözleşme değeri
    
#     # Piyasa fiyatını al
#     ticker = marketDataAPI.get_ticker(instId=f'{coin_pair}-USDT-SWAP')
#     print(ticker)
#     print("mlmds")
#     price = float(ticker["data"][0]["last"])

#     # Dolar cinsinden sözleşme değeri
#     dollar_value_per_contract = contract_value * price
#     print(f'Her sözleşmenin dolar karşılığı: {dollar_value_per_contract} USDT')

#     # Kaç sözleşme gerektiğini hesaplayın
#     contract_size = usdt_amount / dollar_value_per_contract

#     # Lot büyüklüğüne göre sözleşme miktarını yuvarlayın
#     adjusted_contract_size = round(contract_size / lot_size) * lot_size
#     print(f'USDT cinsinden {usdt_amount} için ayarlanmış sözleşme sayısı: {adjusted_contract_size}')

#     print(adjusted_contract_size)
    

#     # Long pozisyon açma işlemi
#     order = tradeAPI.place_order(
#         instId=f'{coin_pair}-USDT-SWAP',
#         tdMode='cross',
#         side='buy',
#         posSide="long",
#         ordType='market',
#         sz=str(int(adjusted_contract_size)),
#     )

#     return order

# # Örnek kullanım
# order_response = usdt_to_contract_and_place_order(80, 'XRP')
# print(order_response)

# def usdt_to_contract(usdt, coin):           

#     ticker = marketDataAPI.get_ticker(
#     instId=f"{coin}-USDT-SWAP"
#     )

#     usdtprice = float(ticker["data"][0]["last"])

#     instrument_details = accountAPI.get_instruments(instType="SWAP", instId="XRP-USDT-SWAP")

#     # Sözleşme değerini çekin
#     contract_value =  instrument_details["data"][0]["ctVal"] # Sözleşme değeri
#     contract_currency =  instrument_details["data"][0]["ctValCcy"]# Sözleşme değeri cinsinden para birimi
#     dollar_value_per_contract = usdtprice * float(contract_value)
#     dollar_amount = usdt
#     contract_size = dollar_amount / dollar_value_per_contract

#     contract_size = round(contract_size)

#     return round(contract_size, 1) 

def open_long(price, lev, coin, levMode):
    print("long")

    max_leverage = int(accountAPI.get_instruments(instType="SWAP", instId= f"{coin}-USDT-SWAP")["data"][0]["lever"])

    if lev < max_leverage or lev == max_leverage:
        lev = lev
    elif lev > max_leverage:
        lev = max_leverage

    leverage = accountAPI.set_leverage(
    instId=f"{coin}-USDT-SWAP",
    lever=f"{lev}",
    mgnMode=f"{levMode}"
    )
    contract_size = get_adjusted_contract_size(price, f'{coin}', 6)
    print(contract_size)
    
    order = tradeAPI.place_order(
    instId=f'{coin}-USDT-SWAP',
    posSide= "long",
    tdMode='cross',
    side='buy',
    ordType='market',
    sz= contract_size,
    ccy="USDT"
    )
    print(order)


async def open_short(price, lev, coin, levMode):
    print("short")

    max_leverage = int(accountAPI.get_instruments(instType="SWAP", instId= f"{coin}-USDT-SWAP")["data"][0]["lever"])

    if lev < max_leverage or lev == max_leverage:
        lev = lev
    elif lev > max_leverage:
        lev = max_leverage

    leverage = accountAPI.set_leverage(
    instId=f"{coin}-USDT-SWAP",
    lever=f"{lev}",
    mgnMode=f"{levMode}"
    )
    print(leverage)

    contract_size = get_adjusted_contract_size(price, f'{coin}', 6)
    print(contract_size)
    
    order = tradeAPI.place_order(
    instId=f'{coin}-USDT-SWAP',
    posSide= "short",
    tdMode=f'{levMode}',
    side='sell',
    ordType='market',
    sz= contract_size,
    ccy="USDT"
    )
    print(order)
    await send_message("@jsklurt", "Yeni short işlem, Baba")

def close_position(coin, levMode):

    global position

    print(coin)

    print("close")
    result = tradeAPI.close_positions(
    instId=f"{coin["coin"]}-USDT-SWAP",
    mgnMode=f"{levMode}",
    ccy= "USDT",
    autoCxl= True,
    posSide=coin["side"]
    )

    print(result)

# close_position("GAS", "cross")
# print(accountAPI.get_positions())


# Telegram API kimlik bilgilerinizi girin
api_id = '26229331'
api_hash = '1e4f5b538a909f7bf073581cd3040171'
phone_number = '+905528986800'  # Telegram'a kayıtlı telefon numaranız

# Dinlemek istediğiniz kanalın adı veya ID'si
channel_name_or_id = '@jsklurt'

# Belirli bir kullanıcının user_id'si veya username'i
target_user_id = 'hedef_kullanıcı_id_veya_username'

async def send_message(user_id, message):
    try:
        await client.send_message(user_id, message)
        print(f"Mesaj gönderildi: {message}")
    except Exception as e:
        print(f"Mesaj gönderilirken hata oluştu: {e}")


# Telegram istemcisi oluşturun
client = TelegramClient('session_name', api_id, api_hash)

# Belirli bir kişiden mesaj geldiğinde çalışacak fonksiyon
async def maBot(message):
    print(f"maBot fonksiyonu çağrıldı: {message.message}")
    global position
    m = message.message
    print(type(m))

    if "USDT" in m:
        
        coin = m[2 : m.index("USDT")]
        print(coin)

       
        
        if "🟣" in m:
            print("sell")
            side = "sell"
            await open_short(10, 10, coin, "cross")
            position["coin"] = coin
            position["side"] = "short"

        elif "🟢" in m:
            print("buy")
            side = "buy"
            open_long(10, 10, coin, "cross")
            position["coin"] = coin
            position["side"] = "long"


    elif "Kapattım." in m:
        print(position)
        
        close_position(position, "cross")
        position["coin"] = ""
        position["side"] = ""

    elif "ekleme" in m:
        if position["side"] == "short":
            open_short(10, 10, position["coin"], "cross")
        if position["side"] == "long":
            open_long(10, 10, position["coin"], "cross")

    

async def main():
    # Telegram'a giriş yapın
    await client.start(phone_number)

    # Kanalı dinlemek için event handler ekleyin
    @client.on(events.NewMessage(chats=channel_name_or_id))
    async def handler(event):
        # if event.message.sender_id == target_user_id:
        #     # Belirtilen kullanıcıdan gelen mesaj bulundu, maBot fonksiyonunu çağır


        await send_message('@userinfobot', 'Merhaba! Bu bir test mesajıdır.')
        await maBot(event.message)
        print("mesaj")


    # İstemciyi sürekli çalışır durumda tut
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())
