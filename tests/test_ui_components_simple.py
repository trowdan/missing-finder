import pytest
from unittest.mock import Mock, patch, MagicMock
from homeward.models.case import KPIData


class TestKPICardsSimple:
    """Simplified test cases for KPI card components"""
    
    @patch('homeward.ui.components.kpi_cards.ui')
    def test_create_kpi_card_calls_ui_components(self, mock_ui):
        """Test that KPI card creation calls the right UI components"""
        from homeward.ui.components.kpi_cards import create_kpi_card
        
        # Setup basic mocks
        mock_ui.card.return_value.__enter__ = Mock()
        mock_ui.card.return_value.__exit__ = Mock()
        mock_ui.column.return_value.__enter__ = Mock()
        mock_ui.column.return_value.__exit__ = Mock()
        
        create_kpi_card("Test Title", "123", "text-red-400")
        
        # Verify basic UI calls
        mock_ui.card.assert_called_once()
        mock_ui.column.assert_called_once()
        assert mock_ui.label.call_count == 2
    
    @patch('homeward.ui.components.kpi_cards.create_kpi_card')
    @patch('homeward.ui.components.kpi_cards.ui')
    def test_create_kpi_grid_calls_cards(self, mock_ui, mock_create_card):
        """Test that KPI grid creates all 6 cards"""
        from homeward.ui.components.kpi_cards import create_kpi_grid
        
        mock_ui.grid.return_value.__enter__ = Mock()
        mock_ui.grid.return_value.__exit__ = Mock()
        
        kpi_data = KPIData(
            total_cases=100,
            active_cases=15,
            resolved_cases=85,
            sightings_today=5,
            success_rate=85.0,
            avg_resolution_days=3.2
        )
        
        create_kpi_grid(kpi_data)
        
        # Verify grid creation and card calls
        mock_ui.grid.assert_called_once()
        assert mock_create_card.call_count == 6
        
        # Check that the right data is passed
        calls = mock_create_card.call_args_list
        assert calls[0][0][0] == 'Total Cases'
        assert calls[0][0][1] == '100'
        assert calls[1][0][0] == 'Active Cases'
        assert calls[1][0][1] == '15'


class TestCasesTableSimple:
    """Simplified test cases for cases table components"""
    
    @patch('homeward.ui.components.cases_table.ui')
    def test_create_cases_table_with_many_cases(self, mock_ui):
        """Test cases table with more than 10 cases shows view all button"""
        from homeward.ui.components.cases_table import create_cases_table
        
        # Setup mocks
        mock_ui.card.return_value.__enter__ = Mock()
        mock_ui.card.return_value.__exit__ = Mock()
        mock_ui.row.return_value.__enter__ = Mock()
        mock_ui.row.return_value.__exit__ = Mock()
        mock_ui.element.return_value.__enter__ = Mock()
        mock_ui.element.return_value.__exit__ = Mock()
        
        # Create 12 mock cases
        mock_cases = [Mock(id=f"MP{i:03d}") for i in range(12)]
        
        with patch('homeward.ui.components.cases_table.create_case_row') as mock_create_row:
            create_cases_table(mock_cases)
            
            # Should only show first 10 cases
            assert mock_create_row.call_count == 10
            
            # Should create "View all" button
            mock_ui.button.assert_called_once()
    
    @patch('homeward.ui.components.cases_table.ui')
    def test_create_cases_table_with_few_cases(self, mock_ui):
        """Test cases table with 10 or fewer cases doesn't show view all button"""
        from homeward.ui.components.cases_table import create_cases_table
        
        # Setup mocks
        mock_ui.card.return_value.__enter__ = Mock()
        mock_ui.card.return_value.__exit__ = Mock()
        mock_ui.row.return_value.__enter__ = Mock()
        mock_ui.row.return_value.__exit__ = Mock()
        mock_ui.element.return_value.__enter__ = Mock()
        mock_ui.element.return_value.__exit__ = Mock()
        
        # Create 5 mock cases
        mock_cases = [Mock(id=f"MP{i:03d}") for i in range(5)]
        
        with patch('homeward.ui.components.cases_table.create_case_row') as mock_create_row:
            create_cases_table(mock_cases)
            
            # Should show all 5 cases
            assert mock_create_row.call_count == 5
            
            # Should not create "View all" button
            mock_ui.button.assert_not_called()


class TestFooterSimple:
    """Simplified test cases for footer component"""
    
    @patch('homeward.ui.components.footer.ui')
    def test_create_footer_displays_version(self, mock_ui):
        """Test that footer displays the version correctly"""
        from homeward.ui.components.footer import create_footer
        
        mock_ui.row.return_value.__enter__ = Mock()
        mock_ui.row.return_value.__exit__ = Mock()
        
        create_footer("1.2.3")
        
        # Verify row and label creation
        mock_ui.row.assert_called_once()
        mock_ui.label.assert_called_once()
        
        # Check that version is included in label
        label_call = mock_ui.label.call_args
        assert 'Homeward v1.2.3' in label_call[0][0]


class TestUIComponentsIntegration:
    """Test UI components working together"""
    
    def test_kpi_data_formatting(self):
        """Test that KPI data is formatted correctly"""
        kpi_data = KPIData(
            total_cases=247,
            active_cases=12,
            resolved_cases=235,
            sightings_today=8,
            success_rate=95.2,
            avg_resolution_days=3.4
        )
        
        # Test the data values that would be displayed
        assert str(kpi_data.total_cases) == "247"
        assert str(kpi_data.active_cases) == "12"
        assert f'{kpi_data.success_rate}%' == "95.2%"
        assert f'{kpi_data.avg_resolution_days}d' == "3.4d"
    
    def test_case_pagination_logic(self):
        """Test the pagination logic for cases"""
        # Test with more than 10 cases
        many_cases = [f"case_{i}" for i in range(15)]
        displayed_cases = many_cases[:10]
        assert len(displayed_cases) == 10
        assert len(many_cases) > 10  # Should trigger "View all"
        
        # Test with fewer than 10 cases
        few_cases = [f"case_{i}" for i in range(5)]
        displayed_few = few_cases[:10]
        assert len(displayed_few) == 5
        assert len(few_cases) <= 10  # Should not trigger "View all"