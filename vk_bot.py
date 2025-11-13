from environs import Env
from vkbottle.bot import Bot, Message


async def echo_handler(message: Message):
    await message.answer(message.text)


def main():
    env = Env()
    env.read_env()
    vk_token = env.str("VK_TOKEN")

    bot = Bot(token=vk_token)
    bot.on.message()(echo_handler)

    bot.run_forever()  # Это обычная функция, не корутина


if __name__ == "__main__":
    main()