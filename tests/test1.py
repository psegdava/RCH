import os
import pandas as pd
from tqdm import tqdm
from typing import Tuple
from RCH_module.RCH import get_volumes


def load_data(data_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load data from a excel file and return a DataFrame.

    Args:
        data_path (str): Path to the Excel file.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: DataFrames for 'Viajes' and 'Partidas' sheets.
    """
    xls = pd.ExcelFile(data_path)
    df_viajes = pd.read_excel(xls, 'Viajes')
    df_partidas = pd.read_excel(xls, 'Partidas')

    return df_viajes, df_partidas


def preprocess_data(
        df_viajes: pd.DataFrame, df_partidas: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Preprocess the data by renaming columns and converting types.

    Args:
        df_viajes (pd.DataFrame): DataFrame for 'Viajes'.
        df_partidas (pd.DataFrame): DataFrame for 'Partidas'.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: Preprocessed DataFrames for 'Viajes' and 'Partidas'.
    """
    # Change "Remontable" values to nuemerical
    df_partidas['Remontable'] = df_partidas['Remontable'].map({'NO': 0, 'SI': 1})

    # Calculate the volume for each partida
    df_partidas['Volumen'] = df_partidas['AltoCm'] * df_partidas['AnchoCm'] * df_partidas['LargoCm']

    # Include the mesurements for the "MAXI 45'" container
    df_viajes.loc[df_viajes['TipoEquipo'] == "MAXI 45'", 'AltoCm'] = 259
    df_viajes.loc[df_viajes['TipoEquipo'] == "MAXI 45'", 'LargoCm'] = 1350
    df_viajes.loc[df_viajes['TipoEquipo'] == "MAXI 45'", 'AnchoCm'] = 244
    # Drop unnecessary columns
    df_viajes = df_viajes.drop(['TipoEquipoAltoMetros', 'TipoEquipoAnchoMetros', 'TipoEquipoLongitudMetros'], axis=1)

    # Calculate the total volume for each viaje, the column and add it to the df_viajes
    volumen_total_por_viaje = df_partidas.groupby(by=['CodigoViaje'], as_index=False)['Volumen'].agg('sum')
    volumen_total_por_viaje.rename(columns={'Volumen': 'VolumenCargado'}, inplace=True)
    df_viajes = df_viajes.merge(volumen_total_por_viaje, how='left', on='CodigoViaje')

    # Create the 'VolumenMax' and 'Volumen%' columns
    df_viajes['VolumenMax'] = df_viajes['AltoCm'] * df_viajes['AnchoCm'] * df_viajes['LargoCm']
    df_viajes['Volumen%'] = df_viajes['VolumenCargado'] / df_viajes['VolumenMax'] * 100

    return df_viajes, df_partidas


def select_viajes(df_viajes: pd.DataFrame) -> pd.DataFrame:
    """
    Select specific voyages based on criteria:
    - Container type is "MAXI 45'"
    - PuroVolumetrica is 1
    - FechaCierreViaje is from the last month

    Args:
        df_viajes (pd.DataFrame): DataFrame for 'Viajes'.

    Returns:
        pd.DataFrame: Filtered DataFrame with selected voyages.
    """
    # Select only "MAXI 45'" containers
    filter1 = df_viajes['TipoEquipo'] == "MAXI 45'"
    # Select only containers that are "PuroVolumetrica"
    filter2 = df_viajes['PuroVolumetrica'] == 1
    # Select only containers from last month
    fliter3 = df_viajes['FechaCierreViaje'] >= "2025-05-01"

    # Select only "CodigoViaje", "NumPartidas", "Volumen%" columns
    columns = ['CodigoViaje', 'NumPartidas', 'Volumen%']

    # Select only the resulting lines
    df_viajes_filtered = df_viajes[filter1 & filter2 & fliter3][columns].copy()
    df_viajes_filtered = df_viajes_filtered.reset_index(drop=True)

    return df_viajes_filtered


def save_partidas_for_viaje(
        df_partidas: pd.DataFrame, codigo_viaje: str, dir: str = "test_data/"
    ) -> pd.DataFrame:
    """
    Save the partidas for a specific viaje to an Excel file.

    Args:
        df_partidas (pd.DataFrame): DataFrame for 'Partidas'.
        codigo_viaje (str): The code of the viaje to filter partidas.
        dir (str): Directory to save the Excel file.

    Returns:
        pd.DataFrame: Filtered DataFrame with partidas for the specified viaje.
    """
    # Filter partidas for the specified viaje
    df_partidas_by_viaje = df_partidas[df_partidas['CodigoViaje'] == codigo_viaje].copy()
    df_partidas_by_viaje = df_partidas_by_viaje.reset_index(drop=True)

    # Save the filtered partidas to an Excel file
    output_file = f"{dir}partidas_{codigo_viaje}.xlsx"
    df_partidas_by_viaje.to_excel(output_file, index=False)

    return df_partidas_by_viaje


def save_all_partidas(
        df_viajes_filtered: pd.DataFrame, df_partidas: pd.DataFrame, dir: str = "test_data/"
    ) -> None:
    """
    Save partidas for all filtered voyages to Excel files.

    Args:
        df_viajes_filtered (pd.DataFrame): Filtered DataFrame with selected voyages.
        df_partidas (pd.DataFrame): DataFrame for 'Partidas'.
        dir (str): Directory to save the Excel files.
    """
    # Ensure the directory exists
    if not os.path.exists(dir):
        os.makedirs(dir)

    for codigo_viaje in tqdm(df_viajes_filtered['CodigoViaje'], desc="Saving partidas for voyages"):
        save_partidas_for_viaje(df_partidas, codigo_viaje, dir)


def test_saved_partidas(file_path: str = "test_data/") -> dict:
    """
    Test a saved partida to see if the algorithm works at least
    as good as the done packaging.

    Args:
        file_name (str): Path to the Excel file containing the partida.

    Returns:
        dict: Dictionary with the average percentage of loaded volume for each viaje.
    """
    codigo_viaje = file_path.split('_')[1].split('.')[0]  # Extract the viaje code from the filename
    print(f"\nTesting {codigo_viaje}...")
    avg_pctg, _, _, not_loaded = get_volumes(codigo_viaje, load_type=2, file_path=file_path)
    print(f"Average percentage of loaded volume for {codigo_viaje}: {avg_pctg:.2f}%")
    print(f"Not loaded partidas for {codigo_viaje}: {not_loaded}")


def test_all_saved_partidas(dir: str = "test_data/") -> None:
    """
    Test all the saved partidas to see if the algorithm works at least
    as good as the done packaging.

    Args:
        dir (str): Directory where the partidas Excel files are saved.

    Returns:
        dict: Dictionary with the average percentage of loaded volume for each viaje.
    """
    results = {}
    for file in os.listdir(dir):
        if file.endswith('.xlsx'):
            file_path = os.path.join(dir, file)
            codigo_viaje = file.split('_')[1].split('.')[0]  # Extract the viaje code from the filename
            print(f"\nTesting {codigo_viaje}...")
            avg_pctg, _, _, _ = get_volumes(codigo_viaje, load_type=2, file_path=file_path)
            results[codigo_viaje] = avg_pctg

    return results

if __name__ == "__main__":
    file_name = 'input_total/2024 12 03 Viajes almacen bcn solo mercancia pasada por volumétrica con clonados, ADR y Aduanas.xlsx'
    df_viajes, df_partidas = load_data(file_name)
    print(f"Loaded {len(df_viajes)} voyages and {len(df_partidas)} partidas from {file_name}.")
    df_viajes, df_partidas = preprocess_data(df_viajes, df_partidas)
    print("Data preprocessed successfully.")
    df_viajes_filtered = select_viajes(df_viajes)
    print(f"Selected {len(df_viajes_filtered)} voyages based on criteria.")
    save_all_partidas(df_viajes_filtered, df_partidas)
    print("Partidas saved for all selected voyages.")

    # results = test_saved_partidas()
