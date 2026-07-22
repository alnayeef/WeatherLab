from pathlib import Path
import pandas as pd


class StationDB:

    def __init__(self,
                 path=None):

        if path is None:
            path = (
                Path(__file__)
                .resolve()
                .parent.parent
                / "data"
                / "stations.parquet"
            )

        self.df = pd.read_parquet(path)

        self.df["wmo"] = self.df["wmo"].astype(str)

    def lookup_wmo(self, wmo):

        result = self.df[
            self.df["wmo"] == str(wmo)
        ]

        if len(result) == 0:
            return None

        return result.iloc[0].to_dict()