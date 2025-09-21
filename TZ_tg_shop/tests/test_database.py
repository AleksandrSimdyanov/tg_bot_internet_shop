import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.database import requests as rq


class TestDatabaseRequests:
    """Тесты для функций базы данных с моками"""

    @pytest.mark.asyncio
    async def test_add_product(self):
        """Тест добавления товара с моком сессии"""
        with patch.object(rq, 'async_session') as mock_session:
            mock_session.return_value.__aenter__.return_value = AsyncMock()
            mock_session.return_value.__aexit__.return_value = AsyncMock()

            # Мокаем коммит и refresh
            mock_commit = AsyncMock()
            mock_refresh = AsyncMock()
            mock_session.return_value.__aenter__.return_value.commit = mock_commit
            mock_session.return_value.__aenter__.return_value.refresh = mock_refresh

            # Мокаем добавление продукта
            mock_product = MagicMock()
            mock_session.return_value.__aenter__.return_value.add.return_value = None

            product = await rq.add_product(
                name="New Product",
                info="New Description",
                photo="new.jpg",
                price=2000,
                type_id=1
            )

            assert product is not None
            mock_commit.assert_called_once()
            mock_refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_product_by_id(self):
        """Тест получения товара по ID"""
        with patch.object(rq, 'async_session') as mock_session:
            # Мокаем сессию и результат запроса
            mock_scalar = AsyncMock(return_value=MagicMock())
            mock_session.return_value.__aenter__.return_value.scalar = mock_scalar

            product = await rq.get_product_by_id(1)

            assert product is not None
            mock_scalar.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_product_by_id_not_found(self):
        """Тест получения несуществующего товара"""
        with patch.object(rq, 'async_session') as mock_session:
            # Мокаем пустой результат
            mock_scalar = AsyncMock(return_value=None)
            mock_session.return_value.__aenter__.return_value.scalar = mock_scalar

            product = await rq.get_product_by_id(999)

            assert product is None
            mock_scalar.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_product(self):
        """Тест обновления товара"""
        with patch.object(rq, 'async_session') as mock_session:
            # Мокаем execute и коммит
            mock_execute = AsyncMock()
            mock_commit = AsyncMock()
            mock_session.return_value.__aenter__.return_value.execute = mock_execute
            mock_session.return_value.__aenter__.return_value.commit = mock_commit

            # Мокаем успешное выполнение
            mock_execute.return_value.rowcount = 1

            success = await rq.update_product(1, name="Updated Product")

            assert success is True
            mock_execute.assert_called_once()
            mock_commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_product_not_found(self):
        """Тест обновления несуществующего товара"""
        with patch.object(rq, 'async_session') as mock_session:
            mock_execute = AsyncMock()
            mock_commit = AsyncMock()
            mock_session.return_value.__aenter__.return_value.execute = mock_execute
            mock_session.return_value.__aenter__.return_value.commit = mock_commit

            # Мокаем неудачное выполнение
            mock_execute.return_value.rowcount = 0

            success = await rq.update_product(999, name="Not Found")

            assert success is False
            mock_execute.assert_called_once()
            mock_commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_product(self):
        """Тест удаления товара"""
        with patch.object(rq, 'async_session') as mock_session:
            mock_execute = AsyncMock()
            mock_commit = AsyncMock()
            mock_session.return_value.__aenter__.return_value.execute = mock_execute
            mock_session.return_value.__aenter__.return_value.commit = mock_commit

            # Мокаем успешное удаление
            mock_execute.return_value.rowcount = 1

            success = await rq.delete_product(1)

            assert success is True
            mock_execute.assert_called_once()
            mock_commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_product_not_found(self):
        """Тест удаления несуществующего товара"""
        with patch.object(rq, 'async_session') as mock_session:
            mock_execute = AsyncMock()
            mock_commit = AsyncMock()
            mock_session.return_value.__aenter__.return_value.execute = mock_execute
            mock_session.return_value.__aenter__.return_value.commit = mock_commit

            # Мокаем неудачное удаление
            mock_execute.return_value.rowcount = 0

            success = await rq.delete_product(999)

            assert success is False
            mock_execute.assert_called_once()
            mock_commit.assert_called_once()


class TestDatabaseErrorHandling:
    """Тесты обработки ошибок базы данных"""

    @pytest.mark.asyncio
    async def test_database_connection_error(self):
        """Тест ошибки подключения к базе данных"""
        with patch.object(rq, 'async_session') as mock_session:
            # Мокаем ошибку при подключении
            mock_session.return_value.__aenter__.side_effect = Exception("Connection failed")

            with pytest.raises(Exception, match="Connection failed"):
                await rq.get_product_by_id(1)

    @pytest.mark.asyncio
    async def test_database_query_error(self):
        """Тест ошибки выполнения запроса"""
        with patch.object(rq, 'async_session') as mock_session:
            # Мокаем ошибку при выполнении запроса
            mock_session.return_value.__aenter__.return_value.scalar.side_effect = Exception("Query failed")

            with pytest.raises(Exception, match="Query failed"):
                await rq.get_product_by_id(1)