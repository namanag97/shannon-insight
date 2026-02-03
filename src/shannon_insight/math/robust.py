"""Robust statistics: MAD, modified z-scores, IQR, isolation forest."""

from typing import List, Optional, Union

import numpy as np


class RobustStatistics:
    """Robust statistical methods resistant to outliers."""

    @staticmethod
    def median_absolute_deviation(values: Union[List[float], np.ndarray]) -> float:
        """
        Median Absolute Deviation: MAD = median(|x_i - median(x)|).

        Args:
            values: List or array of values

        Returns:
            MAD value
        """
        median_val = np.median(values)

        if isinstance(values, np.ndarray):
            deviations = np.abs(values - median_val)
        else:
            deviations = [abs(x - median_val) for x in values]

        return float(np.median(deviations))

    @staticmethod
    def modified_z_score(
        values: Union[List[float], np.ndarray], threshold: float = 3.5
    ) -> List[float]:
        """
        Modified z-scores using MAD (robust to outliers).

        M_i = 0.6745 * (x_i - median) / MAD

        Args:
            values: List of values
            threshold: Outlier threshold (default 3.5)

        Returns:
            List of modified z-scores
        """
        median_val = float(np.median(values))
        mad = RobustStatistics.median_absolute_deviation(values)

        if mad == 0:
            return [0.0] * len(values)

        constant = 0.6745  # Normal distribution consistency constant
        return [constant * (x - median_val) / mad for x in values]

    @staticmethod
    def iqr_outliers(values: List[float], multiplier: float = 1.5) -> List[bool]:
        """
        Detect outliers using Interquartile Range.

        Outlier if x < Q1 - k*IQR or x > Q3 + k*IQR

        Args:
            values: List of values
            multiplier: IQR multiplier (default 1.5)

        Returns:
            List of booleans indicating outliers
        """
        q1 = float(np.percentile(values, 25))
        q3 = float(np.percentile(values, 75))
        iqr = q3 - q1

        lower_bound = q1 - multiplier * iqr
        upper_bound = q3 + multiplier * iqr

        return [(x < lower_bound or x > upper_bound) for x in values]

    @staticmethod
    def isolation_forest_outliers(
        values: np.ndarray, contamination: Optional[float] = 0.1
    ) -> np.ndarray:
        """
        Detect outliers using isolation forest.

        Args:
            values: Array of values
            contamination: Expected proportion of outliers

        Returns:
            Boolean array indicating outliers
        """
        try:
            from sklearn.ensemble import IsolationForest

            contamination_val = "auto" if contamination is None else contamination
            clf = IsolationForest(contamination=contamination_val, random_state=42)
            outliers = clf.fit_predict(values.reshape(-1, 1))
            return np.array([o == -1 for o in outliers])

        except (ImportError, Exception):
            return np.array(
                RobustStatistics.iqr_outliers(
                    values.tolist() if hasattr(values, "tolist") else list(values)
                )
            )
