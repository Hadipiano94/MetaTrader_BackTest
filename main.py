import MetaTrader5 as mt5
import datetime as dt
import time as ti
import turtle as tr
import _tkinter

"""Constants--------------------------------------------------------------------------------------------"""

MY_USERNAME = "your username"
MY_PASSWORD = "your pass"
MY_BROKER = "your broker"

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 648
SCREEN_BORDER = 30

k_dict = {"USDJPY": 2,
          "GBPUSD": 4,
          "EURUSD": 4,
          "AUDUSD": 4,
          "NZDUSD": 4,
          "USDCAD": 4,
          "USDCHF": 4,
          }

"""Classes----------------------------------------------------------------------------------------------"""


class Price:
    def __init__(self, index, price, repetition):
        self.index = index
        self.price = price
        self.repetition = repetition

    def show_content(self):
        return self.index, self.price, self.repetition


class Order:
    def __init__(self, order_type, order_time: dt.datetime, price, tp, sl, order_k, time_limit=None):
        self.close_time = None
        self.type = order_type  # "sell" for sell, "buy" for buy
        self.time = order_time
        self.price = price
        self.tp = tp
        self.sl = sl
        self.open = True
        self.success = True
        self.profit = 0  # when it's minus means loss
        self.k = order_k
        if time_limit is not None:
            self.time_limit = time_limit  # in hours
        self.expire_time = self.time + dt.timedelta(hours=self.time_limit)

    def get_new_tick(self, new_tick):
        if self.open:
            new_tick_time = dt.datetime.fromtimestamp(new_tick[0])
            if new_tick_time.timestamp() >= self.time.timestamp():
                if self.expire_time.date() == new_tick_time.date() and self.expire_time.hour == new_tick_time.hour:
                    self.open = False
                    if self.type == "buy":
                        self.profit = round(new_tick[1] - self.price, ndigits=k)
                    elif self.type == "sell":
                        self.profit = round(self.price - new_tick[2], ndigits=k)
                    if self.profit <= 0:
                        self.success = False
                        self.sl = new_tick[2]
                        print("-Order Closed at Loss")
                    else:
                        self.tp = new_tick[1]
                        print("-Order Closed at Profit")
                    self.close_time = new_tick_time
                elif self.type == "buy":
                    if round(new_tick[1], ndigits=self.k) == round(self.tp, ndigits=self.k):
                        self.open = False
                        self.success = True
                        self.profit = round(self.tp - self.price, ndigits=k)
                        self.close_time = dt.datetime.fromtimestamp(new_tick[0])
                        print("-Order Closed at Profit")
                    elif round(new_tick[2], ndigits=self.k) == round(self.sl, ndigits=self.k):
                        self.open = False
                        self.success = False
                        self.profit = round(self.sl - self.price, ndigits=k)
                        self.close_time = dt.datetime.fromtimestamp(new_tick[0])
                        print("-Order Closed at Loss")
                elif self.type == "sell":
                    if round(new_tick[2], ndigits=self.k) == round(self.tp, ndigits=self.k):
                        self.open = False
                        self.success = True
                        self.profit = round(self.price - self.tp, ndigits=k)
                        self.close_time = dt.datetime.fromtimestamp(new_tick[0])
                        print("-Order Closed at Profit")
                    elif round(new_tick[1], ndigits=self.k) == round(self.sl, ndigits=self.k):
                        self.open = False
                        self.success = False
                        self.profit = round(self.price - self.sl, ndigits=k)
                        self.close_time = dt.datetime.fromtimestamp(new_tick[0])
                        print("-Order Closed at Loss")


"""Functions--------------------------------------------------------------------------------------------"""


def start_mt5(username, password, server):
    username = int(username)
    password = str(password)
    trading_server = str(server)

    if mt5.initialize(login=username, password=password, server=trading_server):
        if mt5.login(login=username, password=password, server=trading_server):
            return True
        else:
            print("Login Fail")
            quit()
            return PermissionError
    else:
        print("MT5 Initialization Failed")
        quit()
        return ConnectionAbortedError


def show_chart(data_list, max_price_f, min_price_f, the_color, pen_size=1):
    global TEST_START, TEST_FINISH
    if len(data_list) != 0 and max([data[1] for data in data_list]) - min([data[1] for data in data_list]) != 0:
        start_timestamp = TEST_START.timestamp()
        finish_timestamp = TEST_FINISH.timestamp()
        my_turtle_1 = tr.Turtle()
        my_turtle_1.hideturtle()
        my_turtle_1.penup()
        my_turtle_1.color("black")
        my_turtle_1.speed(0)
        my_turtle_1.goto(x=-((SCREEN_WIDTH / 2) - SCREEN_BORDER), y=(SCREEN_HEIGHT / 2) - SCREEN_BORDER)
        my_turtle_1.setheading(90)
        my_turtle_1.stamp()
        my_turtle_1.pendown()
        my_turtle_1.goto(x=-((SCREEN_WIDTH / 2) - SCREEN_BORDER), y=-((SCREEN_HEIGHT / 2) - SCREEN_BORDER))
        my_turtle_1.goto(x=((SCREEN_WIDTH / 2) - SCREEN_BORDER), y=-((SCREEN_HEIGHT / 2) - SCREEN_BORDER))
        my_turtle_1.setheading(0)
        my_turtle_1.stamp()
        my_turtle_1.penup()
        my_turtle_1.speed(0)

        my_turtle_1.color(the_color)
        my_turtle_1.pensize(pen_size)
        for data in data_list:
            data_timestamp = data[0].timestamp()
            try:
                my_turtle_1.goto(
                    x=(data_timestamp - start_timestamp) * (
                                (SCREEN_WIDTH - (2 * SCREEN_BORDER)) / (finish_timestamp - start_timestamp)) - (
                                  SCREEN_WIDTH / 2 - SCREEN_BORDER),
                    y=(data[1] - min_price_f) *
                      ((SCREEN_HEIGHT - (2 * SCREEN_BORDER)) / (max_price_f - min_price_f)) -
                      ((SCREEN_HEIGHT / 2) - SCREEN_BORDER))
            except _tkinter.TclError:
                pass
            my_turtle_1.pendown()
        try:
            my_turtle_1.penup()
        except _tkinter.TclError:
            pass


def show_market_profile(price_list_f,
                        max_key_f,
                        min_key_f,
                        max_value_f,
                        min_value_f,
                        max_list_f,
                        min_list_f,
                        max_max_list_f,
                        min_min_list_f,
                        max_line=False):
    my_turtle_1 = tr.Turtle()
    my_turtle_1.hideturtle()
    my_turtle_1.penup()
    my_turtle_1.pensize(1)
    my_turtle_1.speed(0)
    tint_start = (180, 180, 180)  # RGB
    tint_finish = (255, 0, 0)  # RGB
    exp_num = 2
    for price in price_list_f:
        my_turtle_1.color((round(tint_start[0] + (((price.repetition ** exp_num) - (min_value_f ** exp_num)) * (
                    (tint_finish[0] - tint_start[0]) / ((max_value_f ** exp_num) - (min_value_f ** exp_num))))),  # R
                           round(tint_start[1] + (((price.repetition ** exp_num) - (min_value_f ** exp_num)) * (
                                       (tint_finish[1] - tint_start[1]) / (
                                           (max_value_f ** exp_num) - (min_value_f ** exp_num))))),  # G
                           round(tint_start[2] + (((price.repetition ** exp_num) - (min_value_f ** exp_num)) * (
                                       (tint_finish[2] - tint_start[2]) / (
                                           (max_value_f ** exp_num) - (min_value_f ** exp_num)))))  # B
                           ))
        my_turtle_1.goto(x=-((SCREEN_WIDTH / 2) - SCREEN_BORDER), y=-((SCREEN_HEIGHT / 2) - SCREEN_BORDER) + (
                    (price.price - min_key_f) * ((SCREEN_HEIGHT - 2 * SCREEN_BORDER) / (max_key_f - min_key_f))))
        my_turtle_1.pendown()
        my_turtle_1.goto(x=-((SCREEN_WIDTH / 2) - SCREEN_BORDER) + ((price.repetition - min_value_f) * (
                    (SCREEN_WIDTH - (2 * SCREEN_BORDER)) / (max_value_f - min_value_f))),
                         y=-((SCREEN_HEIGHT / 2) - SCREEN_BORDER) + ((price.price - min_key_f) * (
                                     (SCREEN_HEIGHT - 2 * SCREEN_BORDER) / (max_key_f - min_key_f))))
        if price in max_list_f:
            my_turtle_1.color("blue")
            my_turtle_1.dot(4)
            my_turtle_1.pendown()
            my_turtle_1.goto(x=(SCREEN_WIDTH / 2) - SCREEN_BORDER, y=-((SCREEN_HEIGHT / 2) - SCREEN_BORDER) + (
                        (price.price - min_key_f) * ((SCREEN_HEIGHT - 2 * SCREEN_BORDER) / (max_key_f - min_key_f))))
        elif price in min_list_f:
            my_turtle_1.color("light green")
            if price in min_min_list_f:
                my_turtle_1.color("green")
            my_turtle_1.dot(4)
            my_turtle_1.pendown()
            my_turtle_1.goto(x=(SCREEN_WIDTH / 2) - SCREEN_BORDER, y=-((SCREEN_HEIGHT / 2) - SCREEN_BORDER) + (
                        (price.price - min_key_f) * ((SCREEN_HEIGHT - 2 * SCREEN_BORDER) / (max_key_f - min_key_f))))
        my_turtle_1.penup()
    if max_line:
        my_turtle_1.color("green")
        for price in max_list_f:
            my_turtle_1.goto(x=-((SCREEN_WIDTH / 2) - SCREEN_BORDER) + ((price.repetition - min_value_f) * (
                        (SCREEN_WIDTH - (2 * SCREEN_BORDER)) / (max_value_f - min_value_f))),
                             y=-((SCREEN_HEIGHT / 2) - SCREEN_BORDER) + ((price.price - min_key_f) * (
                                         (SCREEN_HEIGHT - 2 * SCREEN_BORDER) / (max_key_f - min_key_f))))
            my_turtle_1.pendown()
    my_turtle_1.penup()
    for price in max_max_list_f:
        my_turtle_1.color("blue")
        my_turtle_1.goto(x=-((SCREEN_WIDTH / 2) - SCREEN_BORDER) + ((price.repetition - min_value_f) * (
                    (SCREEN_WIDTH - (2 * SCREEN_BORDER)) / (max_value_f - min_value_f))),
                         y=-((SCREEN_HEIGHT / 2) - SCREEN_BORDER) + ((price.price - min_key_f) * (
                                     (SCREEN_HEIGHT - 2 * SCREEN_BORDER) / (max_key_f - min_key_f))))
        my_turtle_1.dot(6)


def show_trade(order_list_f, max_key_f, min_key_f):
    global TEST_START, TEST_FINISH
    start_timestamp = TEST_START.timestamp()
    finish_timestamp = TEST_FINISH.timestamp()
    my_turtle_1 = tr.Turtle()
    my_turtle_1.hideturtle()
    my_turtle_1.penup()
    my_turtle_1.speed(0)
    for order_f in order_list_f:

        order_timestamp = order_f.time.timestamp()

        if order_f.type == "buy":
            my_turtle_1.goto(x=-((SCREEN_WIDTH / 2) - SCREEN_BORDER) + ((order_timestamp - start_timestamp) * (
                        (SCREEN_WIDTH - (2 * SCREEN_BORDER)) / (finish_timestamp - start_timestamp))),
                             y=-((SCREEN_HEIGHT / 2) - SCREEN_BORDER) + ((order_f.price - min_key_f) * (
                                         (SCREEN_HEIGHT - 2 * SCREEN_BORDER) / (max_key_f - min_key_f))))
            my_turtle_1.color("blue")
            my_turtle_1.setheading(90)
            my_turtle_1.stamp()
            my_turtle_1.color("grey")
            my_turtle_1.pendown()
            if not order_f.open:
                order_close_timestamp = order_f.close_time.timestamp()
                if order_f.success:
                    my_turtle_1.goto(x=-((SCREEN_WIDTH / 2) - SCREEN_BORDER) + (
                                (order_close_timestamp - start_timestamp) * (
                                    (SCREEN_WIDTH - (2 * SCREEN_BORDER)) / (finish_timestamp - start_timestamp))),
                                     y=-((SCREEN_HEIGHT / 2) - SCREEN_BORDER) + ((order_f.tp - min_key_f) * (
                                                 (SCREEN_HEIGHT - 2 * SCREEN_BORDER) / (max_key_f - min_key_f))))
                else:
                    my_turtle_1.goto(x=-((SCREEN_WIDTH / 2) - SCREEN_BORDER) + (
                            (order_close_timestamp - start_timestamp) * (
                            (SCREEN_WIDTH - (2 * SCREEN_BORDER)) / (finish_timestamp - start_timestamp))),
                                     y=-((SCREEN_HEIGHT / 2) - SCREEN_BORDER) + ((order_f.sl - min_key_f) * (
                                             (SCREEN_HEIGHT - 2 * SCREEN_BORDER) / (max_key_f - min_key_f))))
                my_turtle_1.penup()
                my_turtle_1.color("red")
                my_turtle_1.setheading(270)
                my_turtle_1.stamp()

        elif order_f.type == "sell":
            my_turtle_1.goto(x=-((SCREEN_WIDTH / 2) - SCREEN_BORDER) + ((order_timestamp - start_timestamp) * (
                        (SCREEN_WIDTH - (2 * SCREEN_BORDER)) / (finish_timestamp - start_timestamp))),
                             y=-((SCREEN_HEIGHT / 2) - SCREEN_BORDER) + ((order_f.price - min_key_f) * (
                                         (SCREEN_HEIGHT - 2 * SCREEN_BORDER) / (max_key_f - min_key_f))))
            my_turtle_1.color("red")
            my_turtle_1.setheading(270)
            my_turtle_1.stamp()
            my_turtle_1.color("grey")
            my_turtle_1.pendown()
            if not order_f.open:
                order_close_timestamp = order_f.close_time.timestamp()
                if order_f.success:
                    my_turtle_1.goto(x=-((SCREEN_WIDTH / 2) - SCREEN_BORDER) + (
                                (order_close_timestamp - start_timestamp) * (
                                    (SCREEN_WIDTH - (2 * SCREEN_BORDER)) / (finish_timestamp - start_timestamp))),
                                     y=-((SCREEN_HEIGHT / 2) - SCREEN_BORDER) + ((order_f.tp - min_key_f) * (
                                                 (SCREEN_HEIGHT - 2 * SCREEN_BORDER) / (max_key_f - min_key_f))))
                else:
                    my_turtle_1.goto(x=-((SCREEN_WIDTH / 2) - SCREEN_BORDER) + (
                            (order_close_timestamp - start_timestamp) * (
                            (SCREEN_WIDTH - (2 * SCREEN_BORDER)) / (finish_timestamp - start_timestamp))),
                                     y=-((SCREEN_HEIGHT / 2) - SCREEN_BORDER) + ((order_f.sl - min_key_f) * (
                                             (SCREEN_HEIGHT - 2 * SCREEN_BORDER) / (max_key_f - min_key_f))))
                my_turtle_1.penup()
                my_turtle_1.color("blue")
                my_turtle_1.setheading(90)
                my_turtle_1.stamp()


def create_data_list(candle_list, ohlc="close"):
    ohlc = ohlc.lower()
    if ohlc == "open":
        index = 1
    elif ohlc == "high":
        index = 2
    elif ohlc == "low":
        index = 3
    else:
        index = 4

    data_list = [[dt.datetime.fromtimestamp(item[0]), item[index]] for item in candle_list]
    return data_list


"""Test Constants---------------------------------------------------------------------------------------"""

SYMBOL = "GBPUSD"
TIME_FRAME = mt5.TIMEFRAME_H1

TP = 70  # in pips
SL = 50

TEST_START = dt.datetime(year=2023, month=1, day=1)
TEST_FINISH = dt.datetime(year=2023, month=2, day=1)
TEST_PERIOD = TEST_FINISH - TEST_START

"""MT5 Initialization-----------------------------------------------------------------------------------"""

start_mt5(MY_USERNAME, MY_PASSWORD, MY_BROKER)
print(f"{mt5.terminal_info()}\n{mt5.version()}\n")

print("-Getting Data from MetaTrader5")

# getting test data
test_data_ticks = mt5.copy_ticks_range(SYMBOL, TEST_START, TEST_FINISH, mt5.COPY_TICKS_ALL)
print(*[dt.datetime.fromtimestamp(tick[0]) for tick in test_data_ticks[:1]], sep="\n")
# getting the candles
test_candles = mt5.copy_rates_range(SYMBOL, TIME_FRAME, TEST_START, TEST_FINISH)
print(*[dt.datetime.fromtimestamp(candle[0]) for candle in test_candles[:1]], sep="\n")
mt5.shutdown()
print("-MetaTrader Shut Down")

"""Data Analysis----------------------------------------------------------------------------------------"""

# Turtle screen to show the data
screen = tr.Screen()
screen.setup(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, startx=0, starty=0)
tr.colormode(255)

# just for showing on the chart
candles_list_open = create_data_list(test_candles, "open")
candles_list_close = create_data_list(test_candles, "close")
candles_list_high = create_data_list(test_candles, "high")
candles_list_low = create_data_list(test_candles, "low")

print("Test Starts!----------------------------------------------------\n")

order_list = []
current_day = TEST_START
k = k_dict[SYMBOL]
op_start_time = ti.time()
price_7 = 0
price_10 = 0
for candle in test_candles:
    candle_time = dt.datetime.fromtimestamp(candle[0])
    if candle_time.hour == 10:
        price_7 = candle[1]
    elif candle_time.hour == 13:
        price_10 = candle[1]
        if price_7 != 0:
            if price_10 > price_7:
                order = Order("sell",
                              order_time=candle_time,
                              price=round(price_10, ndigits=k),
                              tp=round(price_10 - (TP / (10 ** k)), ndigits=k),
                              sl=round(price_10 + (SL / (10 ** k)), ndigits=k),
                              order_k=k,
                              time_limit=7)
                order_list.append(order)
            elif price_10 < price_7:
                order = Order("buy",
                              order_time=candle_time,
                              price=round(price_10, ndigits=k),
                              tp=round(price_10 + (TP / (10 ** k)), ndigits=k),
                              sl=round(price_10 - (SL / (10 ** k)), ndigits=k),
                              order_k=k,
                              time_limit=7)
                order_list.append(order)
        price_7 = 0
        price_10 = 0

print(f"Order number: {len(order_list)}\n")
for order in order_list:
    print(
        f"{order.type.capitalize()} Order:\n   Open time: {order.time}\n   Price: {order.price}\n   TP: {order.tp}\n   SL: {order.sl}\n")

for tick in test_data_ticks:
    for order in order_list:
        order.get_new_tick(tick)

op_finish_time = ti.time()

# making the Report Text
text = ""
text += "\nOrders Report--------------------------------------------------------------------\n"
text += f"From {TEST_START.date()} to {TEST_FINISH.date()}\n"
text += f"{len(order_list)} Orders were opened, \n{len([order for order in order_list if not order.open])} of them were closed.\n\n"

success_count = 0
profit_sum = 0
for order in order_list:
    if not order.open:
        text += f"{order.type.capitalize()} Order:\n   Open time: {order.time}\n   Close time: {order.close_time}\n   Price: {order.price}\n   TP: {order.tp}\n   SL: {order.sl}\n   Profit: {order.profit}\n   Success: {order.success}\n   Open: {order.open}\n"
        profit_sum += order.profit
        if order.success:
            success_count += 1
    else:
        text += f"{order.type.capitalize()} Order:\n   Open time: {order.time}\n   Close time: Didn't Close\n   Price: {order.price}\n   TP: {order.tp}\n   SL: {order.sl}\n   Profit: {order.profit}\n   Success: {order.success}\n   Open: {order.open}\n"

success_percentage = round((success_count / len(order_list)) * 100, ndigits=2)
text += f"\nSuccess: %{success_percentage}\n"
text += f"Profit: {round(profit_sum * 10000)} pip\n"
duration = op_finish_time - op_start_time
text += f"Total execution time: {round(duration)} Sec."

print(text)
with open(f"BackTest_Ali_Strategy_{SYMBOL}_From_{TEST_START.date()}_To_{TEST_FINISH.date()}.txt", mode="w") as file:
    file.write(text)

print("-Text file is saved")
print("-Test Finished successfully")

# showing data on the screen
# show_chart(candles_list_open, max([i[2] for i in test_candles]), min([i[3] for i in test_candles]), "#9fdf9f")
show_chart(candles_list_close, max([i[2] for i in test_candles]), min([i[3] for i in test_candles]), "#9fdf9f")
# show_chart(candles_list_high, max([i[2] for i in test_candles]), min([i[3] for i in test_candles]), "#006633")
# show_chart(candles_list_low, max([i[2] for i in test_candles]), min([i[3] for i in test_candles]), "#006633")
show_trade(order_list, max([i[2] for i in test_candles]), min([i[3] for i in test_candles]))

screen.exitonclick()
