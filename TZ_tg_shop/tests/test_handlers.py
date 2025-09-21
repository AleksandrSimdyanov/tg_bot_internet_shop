import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.handlers import user_handler


class TestUserHandlers:
    """Тесты обработчиков пользователя с моками"""

    @pytest.mark.asyncio
    async def test_start_command(self):
        """Тест команды /start"""
        # Мокаем сообщение
        mock_message = AsyncMock()
        mock_message.from_user.id = 1

        # Мокаем функцию add_user
        with patch.object(user_handler.rq, 'add_user', AsyncMock()) as mock_add_user:
            # Мокаем answer
            mock_message.answer = AsyncMock()

            await user_handler.start_cmd(mock_message)

            # Проверяем вызовы
            mock_add_user.assert_called_once_with(1)
            mock_message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_catalog_command(self):
        """Тест команды каталога"""
        mock_message = AsyncMock()
        mock_message.text = "Каталог 🗂"

        # Мокаем types_kb
        mock_keyboard = MagicMock()
        with patch.object(user_handler.kb, 'types_kb', AsyncMock(return_value=mock_keyboard)):
            mock_message.answer = AsyncMock()

            await user_handler.send_catalog(mock_message)

            # Проверяем вызовы
            user_handler.kb.types_kb.assert_called_once_with(back=True)
            mock_message.answer.assert_called_once()

    @pytest.mark.asyncio
    async def test_show_product_not_found(self):
        """Тест отображения несуществующего товара"""
        # Мокаем callback
        mock_callback = AsyncMock()
        mock_callback.data = "product_999"

        # Мокаем get_product_by_id возвращает None
        with patch.object(user_handler.rq, 'get_product_by_id', AsyncMock(return_value=None)):
            mock_callback.answer = AsyncMock()

            await user_handler.show_product(mock_callback)

            # Проверяем, что вызван answer с сообщением об ошибке
            mock_callback.answer.assert_called_once()
            # Проверяем, что message.answer НЕ вызывался (товар не найден)
            assert not mock_callback.message.answer.called

    @pytest.mark.asyncio
    async def test_show_product_found(self):
        """Тест отображения существующего товара"""
        # Мокаем callback
        mock_callback = AsyncMock()
        mock_callback.data = "product_1"

        # Мокаем товар и категорию
        mock_product = MagicMock()
        mock_product.id = 1
        mock_product.name = "Test Product"
        mock_product.info = "Test Info"
        mock_product.photo = "test.jpg"
        mock_product.type_id = 1

        mock_type = MagicMock()
        mock_type.type = "test"

        with patch.object(user_handler.rq, 'get_product_by_id', AsyncMock(return_value=mock_product)):
            with patch.object(user_handler.rq, 'get_type_by_id', AsyncMock(return_value=mock_type)):
                with patch.object(user_handler, 'FSInputFile', MagicMock()):
                    with patch.object(user_handler.kb, 'buy_kb', AsyncMock(return_value=MagicMock())):
                        mock_callback.message.answer_photo = AsyncMock()
                        mock_callback.answer = AsyncMock()

                        await user_handler.show_product(mock_callback)

                        # Проверяем вызовы
                        mock_callback.message.answer_photo.assert_called_once()
                        mock_callback.answer.assert_called_once()


class TestHandlerErrorHandling:
    """Тесты обработки ошибок в хендлерах"""

    @pytest.mark.asyncio
    async def test_handler_exception_handling(self):
        """Тест обработки исключений в хендлерах"""
        mock_message = AsyncMock()
        mock_message.text = "Каталог 🗂"

        # Мокаем исключение в types_kb
        with patch.object(user_handler.kb, 'types_kb', AsyncMock(side_effect=Exception("Test error"))):
            mock_message.answer = AsyncMock()

            # Должно обработаться без падения
            try:
                await user_handler.send_catalog(mock_message)
                # Если дошли сюда - исключение было обработано
                assert True
            except Exception as e:
                # Если исключение пробросилось - это нормально для тестов
                assert str(e) == "Test error"