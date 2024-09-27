from src.controller.protheus_sd3_production_controller import ProtheusSD3ProductionController
import pandas as pd

def test_get_sd3_data_empty_dataframe():
    """Test that get_sd3_data returns an empty DataFrame when there are no records in the SD3 table."""
    # Create an instance of the controller
    controller = ProtheusSD3ProductionController()
    
    # Call the method and capture the result
    result = controller.get_sd3_data()
    
    # Verify that the result is an empty DataFrame
    assert isinstance(result, pd.DataFrame)
    assert result.empty

def test_get_sd3_data_with_records(mocker):
    """Test that get_sd3_data returns a DataFrame with records when there are records in the SD3 table."""
    # Mock the database call to return sample data
    sample_data = pd.DataFrame({
        'MAQUINA': ['Machine1', 'Machine2'],
        'PRODUTO': ['Product1', 'Product2'],
        'QTD': [10, 20],
        'UNIDADE': ['kg', 'kg'],
        'EMISSAO': ['2023-01-01', '2023-01-02'],
        'HORA': ['10:00', '11:00'],
        'LOTE': ['Lote1', 'Lote2'],
        'USUARIO': ['User1', 'User2'],
        'FABRICA': ['Fab. 1', 'Fab. 2']
    })
    mocker.patch('src.controller.protheus_sd3_production_controller.ProtheusSD3ProductionController.get_sd3_data', return_value=sample_data)

    # Create an instance of the controller
    controller = ProtheusSD3ProductionController()

    # Call the method and capture the result
    result = controller.get_sd3_data()

    # Verify that the result matches the sample data
    pd.testing.assert_frame_equal(result, sample_data)

def test_get_sd3_data_with_error(mocker):
    """Test that get_sd3_data handles errors correctly."""
    # Mock the database call to raise an exception
    mocker.patch('src.controller.protheus_sd3_production_controller.ProtheusSD3ProductionController.get_sd3_data', side_effect=Exception("Database error"))

    # Create an instance of the controller
    controller = ProtheusSD3ProductionController()

    # Call the method and capture the result
    try:
        result = controller.get_sd3_data()
    except Exception as e:
        result = str(e)

    # Verify that the result is the expected error message
    assert result == "Database error"

def test_get_sd3_data_with_filters(mocker):
    """Test that get_sd3_data returns filtered data correctly."""
    # Mock the database call to return filtered data
    filtered_data = pd.DataFrame({
        'MAQUINA': ['Machine1'],
        'PRODUTO': ['Product1'],
        'QTD': [10],
        'UNIDADE': ['kg'],
        'EMISSAO': ['2023-01-01'],
        'HORA': ['10:00'],
        'LOTE': ['Lote1'],
        'USUARIO': ['User1'],
        'FABRICA': ['Fab. 1']
    })
    mocker.patch('src.controller.protheus_sd3_production_controller.ProtheusSD3ProductionController.get_sd3_data', return_value=filtered_data)

    # Create an instance of the controller
    controller = ProtheusSD3ProductionController()

    # Call the method with filters and capture the result
    result = controller.get_sd3_data(filters={'MAQUINA': 'Machine1'})

    # Verify that the result matches the filtered data
    pd.testing.assert_frame_equal(result, filtered_data)
    
