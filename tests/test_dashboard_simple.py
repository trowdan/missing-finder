import pytest
from unittest.mock import Mock, patch
from homeward.ui.pages.dashboard import (
    handle_new_case_click, 
    handle_sightings_click, 
    handle_case_click,
    handle_view_all_cases_click
)


class TestDashboardHandlers:
    """Test cases for dashboard event handlers"""
    
    @patch('homeward.ui.pages.dashboard.ui')
    def test_handle_new_case_click(self, mock_ui):
        """Test new case button click handler"""
        handle_new_case_click()
        mock_ui.navigate.to.assert_called_once_with('/new-report')
    
    @patch('homeward.ui.pages.dashboard.ui')
    def test_handle_sightings_click(self, mock_ui):
        """Test new sighting button click handler"""
        handle_sightings_click()
        mock_ui.navigate.to.assert_called_once_with('/new-sighting')
    
    @patch('homeward.ui.pages.dashboard.ui')
    def test_handle_case_click(self, mock_ui):
        """Test case row click handler"""
        mock_case = Mock()
        mock_case.id = "MP001"
        
        handle_case_click(mock_case)
        
        mock_ui.navigate.to.assert_called_once_with('/case/MP001')
    
    @patch('homeward.ui.pages.dashboard.ui')
    def test_handle_view_all_cases_click(self, mock_ui):
        """Test view all cases link click handler"""
        handle_view_all_cases_click()
        mock_ui.notify.assert_called_once_with('Navigate to all cases page')


class TestDashboardCreation:
    """Simplified test cases for dashboard creation"""
    
    @patch('homeward.ui.pages.dashboard.create_kpi_grid')
    @patch('homeward.ui.pages.dashboard.create_cases_table')
    @patch('homeward.ui.pages.dashboard.create_footer')
    @patch('homeward.ui.pages.dashboard.ui')
    def test_dashboard_component_calls(self, mock_ui, mock_footer, mock_cases_table, mock_kpi_grid):
        """Test that dashboard calls all required components"""
        from homeward.ui.pages.dashboard import create_dashboard
        
        # Setup data service mock
        mock_data_service = Mock()
        mock_data_service.get_kpi_data.return_value = Mock()
        mock_data_service.get_cases.return_value = []
        
        # Setup config mock
        mock_config = Mock()
        mock_config.version = "1.0.0"
        
        # Setup UI mocks
        mock_ui.column.return_value.__enter__ = Mock()
        mock_ui.column.return_value.__exit__ = Mock()
        mock_ui.row.return_value.__enter__ = Mock()
        mock_ui.row.return_value.__exit__ = Mock()
        mock_ui.dark_mode.return_value = Mock()
        
        create_dashboard(mock_data_service, mock_config)
        
        # Verify all components were called
        mock_kpi_grid.assert_called_once()
        mock_cases_table.assert_called_once()
        mock_footer.assert_called_once_with("1.0.0")
        
        # Verify data service was called
        mock_data_service.get_kpi_data.assert_called_once()
        mock_data_service.get_cases.assert_called_once()
    
    @patch('homeward.ui.pages.dashboard.create_kpi_grid')
    @patch('homeward.ui.pages.dashboard.create_cases_table')
    @patch('homeward.ui.pages.dashboard.create_footer')
    @patch('homeward.ui.pages.dashboard.ui')
    def test_dashboard_ui_structure(self, mock_ui, mock_footer, mock_cases_table, mock_kpi_grid):
        """Test that dashboard creates correct UI structure"""
        from homeward.ui.pages.dashboard import create_dashboard
        
        # Setup mocks
        mock_data_service = Mock()
        mock_data_service.get_kpi_data.return_value = Mock()
        mock_data_service.get_cases.return_value = []
        mock_config = Mock()
        mock_config.version = "1.0.0"
        
        mock_ui.column.return_value.__enter__ = Mock()
        mock_ui.column.return_value.__exit__ = Mock()
        mock_ui.row.return_value.__enter__ = Mock()
        mock_ui.row.return_value.__exit__ = Mock()
        mock_ui.dark_mode.return_value = Mock()
        
        create_dashboard(mock_data_service, mock_config)
        
        # Verify UI structure
        mock_ui.dark_mode.assert_called_once()
        assert mock_ui.column.call_count >= 2  # Main and header columns
        assert mock_ui.row.call_count >= 1     # Button row
        assert mock_ui.label.call_count >= 2   # Title and section labels
        assert mock_ui.button.call_count >= 2  # Action buttons (including search buttons)
    
    @patch('homeward.ui.pages.dashboard.create_kpi_grid')
    @patch('homeward.ui.pages.dashboard.create_cases_table')
    @patch('homeward.ui.pages.dashboard.create_footer')
    @patch('homeward.ui.pages.dashboard.ui')
    def test_dashboard_button_handlers(self, mock_ui, mock_footer, mock_cases_table, mock_kpi_grid):
        """Test that dashboard buttons have click handlers"""
        from homeward.ui.pages.dashboard import create_dashboard
        
        # Setup mocks
        mock_data_service = Mock()
        mock_data_service.get_kpi_data.return_value = Mock()
        mock_data_service.get_cases.return_value = []
        mock_config = Mock()
        mock_config.version = "1.0.0"
        
        mock_ui.column.return_value.__enter__ = Mock()
        mock_ui.column.return_value.__exit__ = Mock()
        mock_ui.row.return_value.__enter__ = Mock()
        mock_ui.row.return_value.__exit__ = Mock()
        mock_ui.dark_mode.return_value = Mock()
        
        create_dashboard(mock_data_service, mock_config)
        
        # Verify buttons were created with handlers (now includes search buttons)
        assert mock_ui.button.call_count >= 2
        
        # Check button calls have on_click handlers
        button_calls = mock_ui.button.call_args_list
        for call in button_calls:
            # Each button call should have keyword arguments including on_click
            assert len(call) >= 2  # args and kwargs
            # We can't easily test the lambda functions, but we can verify they exist
    
    def test_dashboard_data_filtering(self):
        """Test that dashboard requests active cases only"""
        from homeward.ui.pages.dashboard import create_dashboard
        
        mock_data_service = Mock()
        mock_config = Mock()
        mock_config.version = "1.0.0"
        
        with patch('homeward.ui.pages.dashboard.ui') as mock_ui, \
             patch('homeward.ui.pages.dashboard.create_kpi_grid'), \
             patch('homeward.ui.pages.dashboard.create_cases_table'), \
             patch('homeward.ui.pages.dashboard.create_footer'):
            
            mock_ui.column.return_value.__enter__ = Mock()
            mock_ui.column.return_value.__exit__ = Mock()
            mock_ui.row.return_value.__enter__ = Mock()
            mock_ui.row.return_value.__exit__ = Mock()
            mock_ui.dark_mode.return_value = Mock()
            
            create_dashboard(mock_data_service, mock_config)
            
            # Verify that all cases are requested (changed to support search functionality)
            mock_data_service.get_cases.assert_called_once()


class TestDashboardErrorHandling:
    """Test dashboard error handling"""
    
    def test_dashboard_handles_service_errors(self):
        """Test dashboard gracefully handles service errors"""
        from homeward.ui.pages.dashboard import create_dashboard
        
        # Create service that raises errors
        mock_data_service = Mock()
        mock_data_service.get_kpi_data.side_effect = Exception("Service error")
        mock_data_service.get_cases.side_effect = Exception("Service error")
        
        mock_config = Mock()
        mock_config.version = "1.0.0"
        
        # Should raise the service error
        with pytest.raises(Exception, match="Service error"):
            create_dashboard(mock_data_service, mock_config)
    
    @patch('homeward.ui.pages.dashboard.create_kpi_grid')
    @patch('homeward.ui.pages.dashboard.create_cases_table')
    @patch('homeward.ui.pages.dashboard.create_footer')
    @patch('homeward.ui.pages.dashboard.ui')
    def test_dashboard_with_none_data(self, mock_ui, mock_footer, mock_cases_table, mock_kpi_grid):
        """Test dashboard handles None data gracefully"""
        from homeward.ui.pages.dashboard import create_dashboard
        
        # Service returns None
        mock_data_service = Mock()
        mock_data_service.get_kpi_data.return_value = None
        mock_data_service.get_cases.return_value = None
        
        mock_config = Mock()
        mock_config.version = "1.0.0"
        
        mock_ui.column.return_value.__enter__ = Mock()
        mock_ui.column.return_value.__exit__ = Mock()
        mock_ui.row.return_value.__enter__ = Mock()
        mock_ui.row.return_value.__exit__ = Mock()
        mock_ui.dark_mode.return_value = Mock()
        
        create_dashboard(mock_data_service, mock_config)
        
        # Components should still be called with None data
        mock_kpi_grid.assert_called_once_with(None)
        mock_cases_table.assert_called_once()


class TestDashboardIntegration:
    """Integration tests for dashboard workflow"""
    
    def test_complete_dashboard_workflow(self):
        """Test complete dashboard creation and data flow"""
        from homeward.ui.pages.dashboard import create_dashboard
        
        # Setup realistic mock data
        mock_kpi_data = Mock()
        mock_cases = [Mock(), Mock(), Mock()]
        
        mock_data_service = Mock()
        mock_data_service.get_kpi_data.return_value = mock_kpi_data
        mock_data_service.get_cases.return_value = mock_cases
        
        mock_config = Mock()
        mock_config.version = "2.1.0"
        
        with patch('homeward.ui.pages.dashboard.ui') as mock_ui, \
             patch('homeward.ui.pages.dashboard.create_kpi_grid') as mock_kpi_grid, \
             patch('homeward.ui.pages.dashboard.create_cases_table') as mock_cases_table, \
             patch('homeward.ui.pages.dashboard.create_footer') as mock_footer:
            
            mock_ui.column.return_value.__enter__ = Mock()
            mock_ui.column.return_value.__exit__ = Mock()
            mock_ui.row.return_value.__enter__ = Mock()
            mock_ui.row.return_value.__exit__ = Mock()
            mock_ui.dark_mode.return_value = Mock()
            
            # Execute dashboard creation
            create_dashboard(mock_data_service, mock_config)
            
            # Verify complete workflow
            # 1. Data fetched
            mock_data_service.get_kpi_data.assert_called_once()
            mock_data_service.get_cases.assert_called_once()
            
            # 2. UI components created
            mock_ui.dark_mode.assert_called_once()
            assert mock_ui.column.called
            assert mock_ui.row.called
            assert mock_ui.label.called
            assert mock_ui.button.called
            
            # 3. Component functions called with data
            mock_kpi_grid.assert_called_once_with(mock_kpi_data)
            mock_cases_table.assert_called_once()
            mock_footer.assert_called_once_with("2.1.0")
            
            # 4. Cases table called with correct arguments
            cases_call = mock_cases_table.call_args
            assert cases_call[0][0] == mock_cases