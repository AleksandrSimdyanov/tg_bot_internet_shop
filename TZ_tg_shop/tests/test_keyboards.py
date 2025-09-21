import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import keyboards as kb
from aiogram.types import InlineKeyboardMarkup


class TestKeyboards:
    """Тесты клавиатур с моками"""

    @pytest.mark.asyncio
    async def test_types_keyboard(self):
        """Тест клавиатуры категорий"""
        # Мокаем получение категорий
        mock_type = MagicMock()
        mock_type.id = 1
        mock_type.ru_name = "Тест"

        with patch.object(kb.rq, 'get_types', AsyncMock(return_value=[mock_type])):
            keyboard = await kb.types_kb()

            assert keyboard is not None
            assert len(keyboard.inline_keyboard) > 0

    @pytest.mark.asyncio
    async def test_products_keyboard(self):
        """Тест клавиатуры товаров"""
        # Мокаем получение товаров
        mock_product = MagicMock()
        mock_product.id = 1
        mock_product.name = "Test Product"

        with patch.object(kb.rq, 'get_products', AsyncMock(return_value=[mock_product])):
            keyboard = await kb.products_kb(1)

            assert keyboard is not None
            assert len(keyboard.inline_keyboard) > 0

    @pytest.mark.asyncio
    async def test_buy_keyboard(self):
        """Тест клавиатуры покупки"""
        # Мокаем получение товара
        mock_product = MagicMock()
        mock_product.id = 1
        mock_product.price = 1000

        with patch.object(kb.rq, 'get_product_by_id', AsyncMock(return_value=mock_product)):
            keyboard = await kb.buy_kb(1)

            assert keyboard is not None
            assert len(keyboard.inline_keyboard) > 0
            assert "1000" in str(keyboard.inline_keyboard[0][0].text)

    @pytest.mark.asyncio
    async def test_buy_keyboard_not_found(self):
        """Тест клавиатуры покупки для несуществующего товара"""
        with patch.object(kb.rq, 'get_product_by_id', AsyncMock(return_value=None)):
            keyboard = await kb.buy_kb(999)

            # Должна вернуться пустая клавиатура
            assert keyboard is not None
            assert isinstance(keyboard, InlineKeyboardMarkup)
            assert len(keyboard.inline_keyboard) == 0

    @pytest.mark.asyncio
    async def test_buy_keyboard_database_error(self):
        """Тест клавиатуры покупки при ошибке базы данных"""
        with patch.object(kb.rq, 'get_product_by_id', AsyncMock(side_effect=Exception("DB error"))):
            keyboard = await kb.buy_kb(1)

            # Должна вернуться пустая клавиатура
            assert keyboard is not None
            assert isinstance(keyboard, InlineKeyboardMarkup)
            assert len(keyboard.inline_keyboard) == 0


class TestKeyboardErrorHandling:
    """Тесты обработки ошибок в клавиатурах"""

    @pytest.mark.asyncio
    async def test_keyboard_with_empty_data(self):
        """Тест клавиатуры с пустыми данными"""
        with patch.object(kb.rq, 'get_types', AsyncMock(return_value=[])):
            keyboard = await kb.types_kb()

            # Должна вернуться валидная клавиатура даже с пустыми данными
            assert keyboard is not None
            # Должна быть кнопка "Назад"
            assert any("back" in btn.callback_data for row in keyboard.inline_keyboard for btn in row)

    @pytest.mark.asyncio
    async def test_keyboard_database_error(self):
        """Тест обработки ошибок базы данных при создании клавиатуры"""
        with patch.object(kb.rq, 'get_types', AsyncMock(side_effect=Exception("DB error"))):
            # Должно обработаться без падения
            keyboard = await kb.types_kb()

            # Должна вернуться валидная клавиатура даже при ошибке
            assert keyboard is not None
            # Должна быть кнопка "Назад"
            assert any("back" in btn.callback_data for row in keyboard.inline_keyboard for btn in row)