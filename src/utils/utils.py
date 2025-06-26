import pandas as pd
from typing import Tuple


def load_data(data_path: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load data from a excel file and return a DataFrame.

    Args:
        data_path (str): Path to the Excel file.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: DataFrames for "Viajes" and "Partidas" sheets.
    """
    xls = pd.ExcelFile(data_path)
    df_viajes = pd.read_excel(xls, "Viajes")
    df_partidas = pd.read_excel(xls, "Partidas")

    return df_viajes, df_partidas


def preprocess_data(
    df_viajes: pd.DataFrame, df_partidas: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Preprocess the data by renaming columns and converting types.

    Args:
        df_viajes (pd.DataFrame): DataFrame for "Viajes".
        df_partidas (pd.DataFrame): DataFrame for "Partidas".

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: Preprocessed DataFrames for "Viajes" and "Partidas".
    """
    # Change "Remontable" values to nuemerical
    df_partidas["Remontable"] = df_partidas["Remontable"].map({"NO": 0, "SI": 1})

    # Calculate the volume for each partida
    df_partidas["Volumen"] = df_partidas["AltoCm"] * df_partidas["AnchoCm"] * df_partidas["LargoCm"]

    # Include the mesurements for the "MAXI 45'" container
    df_viajes.loc[df_viajes["TipoEquipo"] == "MAXI 45'", "AltoCm"] = 259
    df_viajes.loc[df_viajes["TipoEquipo"] == "MAXI 45'", "LargoCm"] = 1350
    df_viajes.loc[df_viajes["TipoEquipo"] == "MAXI 45'", "AnchoCm"] = 244
    # Drop unnecessary columns
    df_viajes = df_viajes.drop(["TipoEquipoAltoMetros", "TipoEquipoAnchoMetros", "TipoEquipoLongitudMetros"], axis=1)

    # Calculate the total volume for each viaje, the column and add it to the df_viajes
    volumen_total_por_viaje = df_partidas.groupby(by=["CodigoViaje"], as_index=False)["Volumen"].agg("sum")
    volumen_total_por_viaje.rename(columns={"Volumen": "VolumenCargado"}, inplace=True)
    df_viajes = df_viajes.merge(volumen_total_por_viaje, how="left", on="CodigoViaje")

    # Create the "VolumenMax" and "Volumen%" columns
    df_viajes["VolumenMax"] = df_viajes["AltoCm"] * df_viajes["AnchoCm"] * df_viajes["LargoCm"]
    df_viajes["Volumen%"] = df_viajes["VolumenCargado"] / df_viajes["VolumenMax"] * 100

    return df_viajes, df_partidas
