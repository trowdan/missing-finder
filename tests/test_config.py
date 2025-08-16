import pytest
import os
from unittest.mock import patch
from homeward.config import AppConfig, DataSource, load_config


class TestDataSource:
    """Test cases for DataSource enum"""
    
    def test_data_source_values(self):
        """Test DataSource enum values"""
        assert DataSource.MOCK.value == "mock"
        assert DataSource.BIGQUERY.value == "bigquery"
    
    def test_data_source_from_string(self):
        """Test creating DataSource from string"""
        assert DataSource("mock") == DataSource.MOCK
        assert DataSource("bigquery") == DataSource.BIGQUERY
    
    def test_data_source_invalid_value(self):
        """Test DataSource with invalid value"""
        with pytest.raises(ValueError):
            DataSource("invalid_source")


class TestAppConfig:
    """Test cases for AppConfig dataclass"""
    
    def test_app_config_creation_minimal(self):
        """Test creating AppConfig with minimal required fields"""
        config = AppConfig(
            data_source=DataSource.MOCK,
            version="1.0.0"
        )
        
        assert config.data_source == DataSource.MOCK
        assert config.version == "1.0.0"
        assert config.bigquery_project_id is None
        assert config.bigquery_dataset is None
        assert config.gcs_bucket_ingestion is None
        assert config.gcs_bucket_processed is None
    
    def test_app_config_creation_complete(self):
        """Test creating AppConfig with all fields"""
        config = AppConfig(
            data_source=DataSource.BIGQUERY,
            version="2.0.0",
            bigquery_project_id="test-project",
            bigquery_dataset="test_dataset",
            gcs_bucket_ingestion="test-ingestion-bucket",
            gcs_bucket_processed="test-processed-bucket"
        )
        
        assert config.data_source == DataSource.BIGQUERY
        assert config.version == "2.0.0"
        assert config.bigquery_project_id == "test-project"
        assert config.bigquery_dataset == "test_dataset"
        assert config.gcs_bucket_ingestion == "test-ingestion-bucket"
        assert config.gcs_bucket_processed == "test-processed-bucket"
    
    def test_app_config_equality(self):
        """Test AppConfig equality comparison"""
        config1 = AppConfig(
            data_source=DataSource.MOCK,
            version="1.0.0",
            bigquery_project_id="test-project"
        )
        
        config2 = AppConfig(
            data_source=DataSource.MOCK,
            version="1.0.0",
            bigquery_project_id="test-project"
        )
        
        assert config1 == config2
    
    def test_app_config_inequality(self):
        """Test AppConfig inequality comparison"""
        config1 = AppConfig(
            data_source=DataSource.MOCK,
            version="1.0.0"
        )
        
        config2 = AppConfig(
            data_source=DataSource.BIGQUERY,
            version="1.0.0"
        )
        
        assert config1 != config2


class TestLoadConfig:
    """Test cases for load_config function"""
    
    def test_load_config_defaults(self):
        """Test loading config with default values"""
        with patch.dict(os.environ, {}, clear=True):
            config = load_config()
            
            assert config.data_source == DataSource.MOCK
            assert config.version == "0.1.0"
            assert config.bigquery_project_id is None
            assert config.bigquery_dataset == "homeward"
            assert config.gcs_bucket_ingestion is None
            assert config.gcs_bucket_processed is None
    
    def test_load_config_from_environment(self):
        """Test loading config from environment variables"""
        env_vars = {
            'HOMEWARD_DATA_SOURCE': 'bigquery',
            'HOMEWARD_VERSION': '2.1.0',
            'HOMEWARD_BIGQUERY_PROJECT_ID': 'my-test-project',
            'HOMEWARD_BIGQUERY_DATASET': 'my_dataset',
            'HOMEWARD_GCS_BUCKET_INGESTION': 'my-ingestion-bucket',
            'HOMEWARD_GCS_BUCKET_PROCESSED': 'my-processed-bucket'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = load_config()
            
            assert config.data_source == DataSource.BIGQUERY
            assert config.version == "2.1.0"
            assert config.bigquery_project_id == "my-test-project"
            assert config.bigquery_dataset == "my_dataset"
            assert config.gcs_bucket_ingestion == "my-ingestion-bucket"
            assert config.gcs_bucket_processed == "my-processed-bucket"
    
    def test_load_config_partial_environment(self):
        """Test loading config with some environment variables set"""
        env_vars = {
            'HOMEWARD_DATA_SOURCE': 'bigquery',
            'HOMEWARD_VERSION': '1.5.0',
            'HOMEWARD_BIGQUERY_PROJECT_ID': 'partial-project'
            # Other variables not set
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = load_config()
            
            assert config.data_source == DataSource.BIGQUERY
            assert config.version == "1.5.0"
            assert config.bigquery_project_id == "partial-project"
            assert config.bigquery_dataset == "homeward"  # Default value
            assert config.gcs_bucket_ingestion is None
            assert config.gcs_bucket_processed is None
    
    def test_load_config_invalid_data_source(self):
        """Test loading config with invalid data source"""
        env_vars = {
            'HOMEWARD_DATA_SOURCE': 'invalid_source'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = load_config()
            
            # Should fallback to MOCK when invalid source is provided
            assert config.data_source == DataSource.MOCK
    
    def test_load_config_case_insensitive_data_source(self):
        """Test that data source is case insensitive"""
        test_cases = [
            ('MOCK', DataSource.MOCK),
            ('mock', DataSource.MOCK),
            ('Mock', DataSource.MOCK),
            ('BIGQUERY', DataSource.BIGQUERY),
            ('bigquery', DataSource.BIGQUERY),
            ('BigQuery', DataSource.BIGQUERY)
        ]
        
        for env_value, expected_source in test_cases:
            env_vars = {'HOMEWARD_DATA_SOURCE': env_value}
            
            with patch.dict(os.environ, env_vars, clear=True):
                config = load_config()
                assert config.data_source == expected_source
    
    def test_load_config_empty_strings(self):
        """Test loading config with empty string environment variables"""
        env_vars = {
            'HOMEWARD_DATA_SOURCE': '',
            'HOMEWARD_VERSION': '',
            'HOMEWARD_BIGQUERY_PROJECT_ID': '',
            'HOMEWARD_BIGQUERY_DATASET': '',
            'HOMEWARD_GCS_BUCKET_INGESTION': '',
            'HOMEWARD_GCS_BUCKET_PROCESSED': ''
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = load_config()
            
            # Empty data source should fallback to mock
            assert config.data_source == DataSource.MOCK
            
            # Empty version should fallback to default (getenv returns empty string, not default)
            assert config.version == ""
            
            # Empty dataset should be empty string (not default when explicitly set to empty)
            assert config.bigquery_dataset == ""
            
            # Empty strings for optional fields should be treated as empty strings, not None
            assert config.bigquery_project_id == ""
            assert config.gcs_bucket_ingestion == ""
            assert config.gcs_bucket_processed == ""
    
    def test_load_config_whitespace_handling(self):
        """Test that whitespace in environment variables is handled"""
        env_vars = {
            'HOMEWARD_DATA_SOURCE': '  bigquery  ',
            'HOMEWARD_VERSION': '  1.0.0  ',
            'HOMEWARD_BIGQUERY_PROJECT_ID': '  test-project  '
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = load_config()
            
            # Data source has whitespace, .lower() is called, but "  bigquery  " becomes "  bigquery  " 
            # which is not a valid enum value, so it falls back to MOCK
            assert config.data_source == DataSource.MOCK
            
            # Other values should preserve whitespace (as they're just strings)
            assert config.version == "  1.0.0  "
            assert config.bigquery_project_id == "  test-project  "
    
    def test_load_config_version_variations(self):
        """Test loading config with different version formats"""
        version_tests = [
            "0.1.0",
            "1.0.0-alpha",
            "2.1.3-beta.1",
            "3.0.0-rc.1+build.123",
            "dev",
            "latest"
        ]
        
        for version in version_tests:
            env_vars = {'HOMEWARD_VERSION': version}
            
            with patch.dict(os.environ, env_vars, clear=True):
                config = load_config()
                assert config.version == version
    
    def test_load_config_reproducibility(self):
        """Test that load_config returns the same result when called multiple times"""
        env_vars = {
            'HOMEWARD_DATA_SOURCE': 'bigquery',
            'HOMEWARD_VERSION': '1.0.0',
            'HOMEWARD_BIGQUERY_PROJECT_ID': 'test-project'
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config1 = load_config()
            config2 = load_config()
            
            assert config1 == config2
            assert config1.data_source == config2.data_source
            assert config1.version == config2.version
            assert config1.bigquery_project_id == config2.bigquery_project_id


class TestConfigurationValidation:
    """Test cases for configuration validation scenarios"""
    
    def test_bigquery_config_completeness(self):
        """Test that BigQuery configuration has required fields"""
        # Valid BigQuery configuration
        config = AppConfig(
            data_source=DataSource.BIGQUERY,
            version="1.0.0",
            bigquery_project_id="test-project",
            bigquery_dataset="test_dataset"
        )
        
        assert config.data_source == DataSource.BIGQUERY
        assert config.bigquery_project_id is not None
        assert config.bigquery_dataset is not None
    
    def test_mock_config_minimal_requirements(self):
        """Test that mock configuration works with minimal fields"""
        config = AppConfig(
            data_source=DataSource.MOCK,
            version="1.0.0"
        )
        
        assert config.data_source == DataSource.MOCK
        # BigQuery fields can be None for mock configuration
        assert config.bigquery_project_id is None
        assert config.bigquery_dataset is None
    
    def test_config_with_production_like_values(self):
        """Test configuration with production-like values"""
        config = AppConfig(
            data_source=DataSource.BIGQUERY,
            version="1.2.3",
            bigquery_project_id="homeward-prod-12345",
            bigquery_dataset="homeward_production",
            gcs_bucket_ingestion="homeward-prod-12345-video-ingestion",
            gcs_bucket_processed="homeward-prod-12345-video-processed"
        )
        
        assert config.data_source == DataSource.BIGQUERY
        assert config.version == "1.2.3"
        assert "prod" in config.bigquery_project_id
        assert "production" in config.bigquery_dataset
        assert "ingestion" in config.gcs_bucket_ingestion
        assert "processed" in config.gcs_bucket_processed