import asyncio

import structlog
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

import logs
from bot import bot
from config import Config, parse_config


async def main() -> None:  # noqa: WPS217
    config: Config = parse_config()
    logs.startup(config.logging)
    logger = structlog.get_logger(__name__)
    await logger.info('App is starting, configs parsed successfully')

    engine = create_async_engine(config.db.uri, **config.db.orm.engine.model_dump())
    session_maker = async_sessionmaker(
        engine, **config.db.orm.session.model_dump(), class_=AsyncSession
    )

    try:
        await asyncio.gather(
            bot(
                config.bot,
                nats_address=config.nats.address,
                session_maker=session_maker,
            ),
        )
    except SystemExit:
        await logger.info('System shutdown')
    except KeyboardInterrupt:
        await logger.info('Shutdown by external call ( KeyboardInterrupt )')
    except Exception as e:
        await logger.exception('Abnormal shutdown detected, critical error happened', e)

if __name__ == '__main__':
    asyncio.run(main())
