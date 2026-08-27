#!/usr/bin/env python3
"""Deterministically build the open predictive/statistical ML research universe.

This is an authoring source, not a completeness claim.  It keeps predictive intent,
statistical identification, model semantics, fitting algorithms, executable kernels,
provider qualification and deployment evidence as separate graph nodes.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EDITION = 1
ACCESSED = "2026-08-25"


def slug(value: str) -> str:
    value = value.lower().replace("+", " plus ")
    return re.sub(r"[^a-z0-9]+", "_", value).strip("_")


def write_json(name: str, value: object) -> None:
    (ROOT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def write_jsonl(name: str, rows: list[dict]) -> None:
    rows = sorted(rows, key=lambda row: next((str(v) for k, v in row.items() if k.endswith("_id")), json.dumps(row, sort_keys=True)))
    (ROOT / name).write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows))


# Primary/original papers, standards, and publisher-maintained reference implementations.
# `curated_primary_reference` means metadata was curated from a primary locator; it does not
# claim that every URL was fetched during this build. The process-mining records named in the
# user's request were independently opened and checked during this research turn.
SOURCE_SPECS = [
    # Cross-family contracts, evaluation, and maintained implementations.
    ("sklearn_user", "scikit-learn User Guide", 2026, "scikit-learn maintainers", "https://scikit-learn.org/stable/user_guide.html", "official_reference", "classical supervised, semi-supervised, calibration, evaluation and inspection APIs"),
    ("statsmodels_user", "statsmodels User Guide", 2026, "statsmodels maintainers", "https://www.statsmodels.org/stable/user-guide.html", "official_reference", "regression, GLM, mixed, duration and time-series interfaces"),
    ("r_stats", "R stats package reference", 2026, "R Core Team", "https://stat.ethz.ch/R-manual/R-devel/library/stats/html/00Index.html", "official_reference", "classical statistical model and test reference interfaces"),
    ("stan_reference", "Stan Reference Manual", 2026, "Stan Development Team", "https://mc-stan.org/docs/reference-manual/", "official_reference", "probabilistic model, inference and diagnostics semantics"),
    ("pymc_api", "PyMC API", 2026, "PyMC Developers", "https://www.pymc.io/projects/docs/en/stable/api.html", "official_reference", "Bayesian model construction and posterior inference interfaces"),
    ("xgboost_docs", "XGBoost documentation", 2026, "XGBoost developers", "https://xgboost.readthedocs.io/en/stable/", "official_reference", "gradient tree boosting objectives, training and prediction"),
    ("lightgbm_docs", "LightGBM documentation", 2026, "LightGBM developers", "https://lightgbm.readthedocs.io/en/stable/", "official_reference", "histogram and leaf-wise gradient boosting implementation"),
    ("catboost_docs", "CatBoost documentation", 2026, "CatBoost developers", "https://catboost.ai/en/docs/", "official_reference", "ordered boosting and categorical feature implementation"),
    ("pytorch_docs", "PyTorch documentation", 2026, "PyTorch contributors", "https://pytorch.org/docs/stable/index.html", "official_reference", "tensor, autograd, optimization and predictive neural execution"),
    ("jax_docs", "JAX documentation", 2026, "JAX contributors", "https://docs.jax.dev/", "official_reference", "differentiable array programs and compilation"),
    ("tensorflow_docs", "TensorFlow API", 2026, "TensorFlow contributors", "https://www.tensorflow.org/api_docs", "official_reference", "tensor, training and serving interfaces"),
    ("onnx_spec", "Open Neural Network Exchange", 2026, "ONNX Working Group", "https://onnx.ai/onnx/", "official_specification", "portable predictive graph and operator semantics"),
    ("treelite_docs", "Treelite documentation", 2026, "Treelite contributors", "https://treelite.readthedocs.io/en/latest/", "official_reference", "tree ensemble compilation and inference"),
    ("river_docs", "River API", 2026, "River maintainers", "https://riverml.xyz/latest/api/overview/", "official_reference", "online learning, drift, anomaly and progressive evaluation"),
    ("mlflow_model", "MLflow Model specification", 2026, "MLflow maintainers", "https://mlflow.org/docs/latest/ml/model/", "official_specification", "model packaging, signatures and flavor boundaries"),
    ("sktime_docs", "sktime API reference", 2026, "sktime maintainers", "https://www.sktime.net/en/stable/api_reference.html", "official_reference", "time-series forecasting, classification and transformation"),
    ("gluonts_docs", "GluonTS documentation", 2026, "GluonTS contributors", "https://ts.gluon.ai/stable/", "official_reference", "probabilistic time-series prediction interfaces"),
    ("lifelines_docs", "lifelines documentation", 2026, "lifelines contributors", "https://lifelines.readthedocs.io/en/latest/", "official_reference", "censored-duration estimators and diagnostics"),
    ("scikit_survival", "scikit-survival User Guide", 2026, "scikit-survival contributors", "https://scikit-survival.readthedocs.io/en/stable/user_guide.html", "official_reference", "survival prediction and evaluation interfaces"),
    ("pytorch_geometric", "PyTorch Geometric documentation", 2026, "PyG contributors", "https://pytorch-geometric.readthedocs.io/en/latest/", "official_reference", "graph predictive operators and loaders"),
    ("dgl_docs", "Deep Graph Library documentation", 2026, "DGL contributors", "https://www.dgl.ai/pages/start.html", "official_reference", "graph neural predictive execution"),
    ("networkx_docs", "NetworkX algorithms", 2026, "NetworkX developers", "https://networkx.org/documentation/stable/reference/algorithms/index.html", "official_reference", "classical graph algorithms and link-analysis primitives"),
    ("pm4py_docs", "PM4Py documentation", 2026, "PM4Py contributors", "https://processintelligence.solutions/pm4py/", "official_reference", "event-data and process-mining implementation surface"),
    ("ocel20", "OCEL 2.0 Specification", 2024, "OCEL Standard authors", "https://www.ocel-standard.org/2.0/ocel20_specification.pdf", "official_specification", "object-centric events, relations and time-varying attributes"),
    ("ogc_sfa", "OGC Simple Features Access", 2011, "Open Geospatial Consortium", "https://www.ogc.org/standards/sfa/", "standard", "geometry, coordinate and topology semantics"),
    ("proj_docs", "PROJ documentation", 2026, "PROJ contributors", "https://proj.org/", "official_reference", "coordinate reference and transformation semantics"),
    ("scipy_signal", "SciPy signal processing reference", 2026, "SciPy contributors", "https://docs.scipy.org/doc/scipy/reference/signal.html", "official_reference", "classical signal transforms and filters"),
    ("opencv_docs", "OpenCV image processing reference", 2026, "OpenCV contributors", "https://docs.opencv.org/4.x/d7/da8/tutorial_table_of_content_imgproc.html", "official_reference", "classical image preprocessing and feature extraction"),
    ("unicode15", "Unicode Normalization Forms", 2026, "Unicode Consortium", "https://www.unicode.org/reports/tr15/", "standard", "text normalization preconditions"),
    ("fairlearn_docs", "Fairlearn User Guide", 2026, "Fairlearn contributors", "https://fairlearn.org/main/user_guide/index.html", "official_reference", "group fairness assessment and mitigation"),
    ("responsible_ai_nist", "NIST AI Risk Management Framework 1.0", 2023, "NIST", "https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf", "standard", "risk governance for predictive systems"),
    ("iso25012", "ISO/IEC 25012 data quality model", 2008, "ISO/IEC", "https://www.iso.org/standard/35736.html", "standard", "input-data quality characteristics"),
    ("fda_gmlp", "Good Machine Learning Practice Guiding Principles", 2021, "FDA Health Canada MHRA", "https://www.fda.gov/medical-devices/software-medical-device-samd/good-machine-learning-practice-medical-device-development-guiding-principles", "regulatory_guidance", "medical predictive lifecycle controls"),
    ("tripo", "TRIPOD Statement", 2015, "TRIPOD Group", "https://www.tripod-statement.org/", "reporting_standard", "prediction model development and validation reporting"),
    ("probatus_docs", "Probatus documentation", 2026, "Probatus contributors", "https://ing-bank.github.io/probatus/", "official_reference", "model validation and interpretation interfaces"),
    # Foundational statistical learning and model families.
    ("glm_nelder", "Generalized Linear Models", 1972, "John Nelder; Robert Wedderburn", "https://doi.org/10.2307/2344614", "primary_paper", "GLM exponential-family and link-function formulation"),
    ("cox_ph", "Regression Models and Life-Tables", 1972, "David Cox", "https://doi.org/10.1111/j.2517-6161.1972.tb00899.x", "primary_paper", "proportional hazards regression"),
    ("kaplan_meier", "Nonparametric Estimation from Incomplete Observations", 1958, "Edward Kaplan; Paul Meier", "https://doi.org/10.1080/01621459.1958.10501452", "primary_paper", "product-limit survival estimator"),
    ("fine_gray", "A Proportional Hazards Model for the Subdistribution of a Competing Risk", 1999, "Jason Fine; Robert Gray", "https://doi.org/10.1080/01621459.1999.10474144", "primary_paper", "competing-risk subdistribution hazards"),
    ("lasso", "Regression Shrinkage and Selection via the Lasso", 1996, "Robert Tibshirani", "https://doi.org/10.1111/j.2517-6161.1996.tb02080.x", "primary_paper", "L1-penalized regression"),
    ("elastic_net", "Regularization and Variable Selection via the Elastic Net", 2005, "Hui Zou; Trevor Hastie", "https://doi.org/10.1111/j.1467-9868.2005.00503.x", "primary_paper", "combined L1/L2 regularization"),
    ("quantile_regression", "Regression Quantiles", 1978, "Roger Koenker; Gilbert Bassett", "https://doi.org/10.2307/1913643", "primary_paper", "conditional quantile regression"),
    ("gam", "Generalized Additive Models", 1986, "Trevor Hastie; Robert Tibshirani", "https://doi.org/10.1214/ss/1177013604", "primary_paper", "smooth additive predictive functions"),
    ("hinge_svm", "Support-Vector Networks", 1995, "Corinna Cortes; Vladimir Vapnik", "https://doi.org/10.1007/BF00994018", "primary_paper", "maximum-margin kernel classification"),
    ("kernel_pca", "Nonlinear Component Analysis as a Kernel Eigenvalue Problem", 1998, "Bernhard Schoelkopf; Alexander Smola; Klaus-Robert Mueller", "https://doi.org/10.1162/089976698300017467", "primary_paper", "kernel feature extraction"),
    ("random_forest", "Random Forests", 2001, "Leo Breiman", "https://doi.org/10.1023/A:1010933404324", "primary_paper", "bagged randomized decision-tree ensembles"),
    ("cart", "Classification and Regression Trees", 1984, "Leo Breiman; Jerome Friedman; Richard Olshen; Charles Stone", "https://doi.org/10.1201/9781315139470", "primary_book", "recursive partitioning model"),
    ("adaboost", "A Decision-Theoretic Generalization of On-Line Learning", 1997, "Yoav Freund; Robert Schapire", "https://doi.org/10.1006/jcss.1997.1504", "primary_paper", "adaptive boosting"),
    ("gradient_boost", "Greedy Function Approximation: A Gradient Boosting Machine", 2001, "Jerome Friedman", "https://doi.org/10.1214/aos/1013203451", "primary_paper", "gradient boosting formulation"),
    ("xgboost_paper", "XGBoost: A Scalable Tree Boosting System", 2016, "Tianqi Chen; Carlos Guestrin", "https://doi.org/10.1145/2939672.2939785", "primary_paper", "regularized scalable tree boosting"),
    ("lightgbm_paper", "LightGBM: A Highly Efficient Gradient Boosting Decision Tree", 2017, "Guolin Ke; Qi Meng; Thomas Finley; Taifeng Wang; Wei Chen; Weidong Ma; Qiwei Ye; Tie-Yan Liu", "https://proceedings.neurips.cc/paper/2017/hash/6449f44a102fde848669bdd9eb6b76fa-Abstract.html", "primary_paper", "histogram, GOSS and EFB tree boosting"),
    ("catboost_paper", "CatBoost: unbiased boosting with categorical features", 2018, "Liudmila Prokhorenkova; Gleb Gusev; Aleksandr Vorobev; Anna Dorogush; Andrey Gulin", "https://proceedings.neurips.cc/paper/2018/hash/14491b756b3a51daac41c24863285549-Abstract.html", "primary_paper", "ordered target statistics and boosting"),
    ("ngboost", "NGBoost: Natural Gradient Boosting for Probabilistic Prediction", 2020, "Tony Duan; Anand Avati; Daisy Ding; Sanjay Basu; Andrew Ng; Alejandro Schuler", "https://proceedings.mlr.press/v119/duan20a.html", "primary_paper", "probabilistic boosting with proper scoring rules"),
    ("bart", "BART: Bayesian Additive Regression Trees", 2010, "Hugh Chipman; Edward George; Robert McCulloch", "https://doi.org/10.1214/09-AOAS285", "primary_paper", "Bayesian tree-sum predictive model"),
    ("gp_rasmussen", "Gaussian Processes for Machine Learning", 2006, "Carl Rasmussen; Christopher Williams", "https://gaussianprocess.org/gpml/", "primary_book", "Gaussian process regression and classification"),
    ("knn_cover", "Nearest Neighbor Pattern Classification", 1967, "Thomas Cover; Peter Hart", "https://doi.org/10.1109/TIT.1967.1053964", "primary_paper", "nearest-neighbor classification"),
    ("platt_scaling", "Probabilistic Outputs for Support Vector Machines", 1999, "John Platt", "https://www.microsoft.com/en-us/research/publication/probabilistic-outputs-for-support-vector-machines-and-comparisons-to-regularized-likelihood-methods/", "primary_paper", "sigmoid score calibration"),
    ("isotonic_cal", "Transforming Classifier Scores into Accurate Multiclass Probability Estimates", 2002, "Bianca Zadrozny; Charles Elkan", "https://doi.org/10.1145/775047.775151", "primary_paper", "isotonic and pairwise calibration"),
    ("temperature_scaling", "On Calibration of Modern Neural Networks", 2017, "Chuan Guo; Geoff Pleiss; Yu Sun; Kilian Weinberger", "https://proceedings.mlr.press/v70/guo17a.html", "primary_paper", "temperature scaling and neural calibration"),
    ("beta_calibration", "Beyond sigmoids: How to obtain well-calibrated probabilities", 2017, "Meelis Kull; Telmo Silva Filho; Peter Flach", "https://doi.org/10.1214/17-EJS1338SI", "primary_paper", "beta calibration"),
    ("stacking", "Stacked Generalization", 1992, "David Wolpert", "https://doi.org/10.1016/S0893-6080(05)80023-1", "primary_paper", "out-of-fold ensemble stacking"),
    ("super_learner", "Super Learner", 2007, "Mark van der Laan; Eric Polley; Alan Hubbard", "https://doi.org/10.2202/1544-6115.1309", "primary_paper", "cross-validated ensemble selection"),
    # Ranking and recommendation.
    ("ranksvm", "Optimizing Search Engines Using Clickthrough Data", 2002, "Thorsten Joachims", "https://doi.org/10.1145/775047.775067", "primary_paper", "pairwise large-margin learning to rank"),
    ("ranknet", "Learning to Rank using Gradient Descent", 2005, "Chris Burges; Tal Shaked; Erin Renshaw; Ari Lazier; Matt Deeds; Nicole Hamilton; Greg Hullender", "https://www.microsoft.com/en-us/research/publication/learning-to-rank-using-gradient-descent/", "primary_paper", "pairwise neural ranking objective"),
    ("lambdarank", "From RankNet to LambdaRank to LambdaMART", 2010, "Chris Burges", "https://www.microsoft.com/en-us/research/publication/from-ranknet-to-lambdarank-to-lambdamart-an-overview/", "primary_report", "metric-directed ranking gradients"),
    ("listnet", "Learning to Rank: From Pairwise Approach to Listwise Approach", 2007, "Zhe Cao; Tao Qin; Tie-Yan Liu; Ming-Feng Tsai; Hang Li", "https://doi.org/10.1145/1273496.1273513", "primary_paper", "listwise ranking objective"),
    ("bpr", "BPR: Bayesian Personalized Ranking from Implicit Feedback", 2009, "Steffen Rendle; Christoph Freudenthaler; Zeno Gantner; Lars Schmidt-Thieme", "https://arxiv.org/abs/1205.2618", "primary_paper", "pairwise implicit-feedback recommendation"),
    ("matrix_factorization", "Matrix Factorization Techniques for Recommender Systems", 2009, "Yehuda Koren; Robert Bell; Chris Volinsky", "https://doi.org/10.1109/MC.2009.263", "primary_paper", "latent-factor recommendation"),
    ("implicit_als", "Collaborative Filtering for Implicit Feedback Datasets", 2008, "Yifan Hu; Yehuda Koren; Chris Volinsky", "https://doi.org/10.1109/ICDM.2008.22", "primary_paper", "weighted alternating least squares for implicit data"),
    ("factorization_machine", "Factorization Machines", 2010, "Steffen Rendle", "https://doi.org/10.1109/ICDM.2010.127", "primary_paper", "sparse interaction prediction"),
    ("slim", "SLIM: Sparse Linear Methods for Top-N Recommender Systems", 2011, "Xia Ning; George Karypis", "https://doi.org/10.1109/ICDM.2011.134", "primary_paper", "sparse item-item recommendation"),
    # Survival, longitudinal, reliability and event history.
    ("random_survival_forest", "Random Survival Forests", 2008, "Hemant Ishwaran; Udaya Kogalur; Eugene Blackstone; Michael Lauer", "https://doi.org/10.1214/08-AOAS169", "primary_paper", "survival tree ensemble"),
    ("deepsurv", "DeepSurv: personalized treatment recommender using a Cox neural network", 2018, "Jared Katzman; Uri Shaham; Alexander Cloninger; Jonathan Bates; Tingting Jiang; Yuval Kluger", "https://doi.org/10.1186/s12874-018-0482-1", "primary_paper", "neural proportional hazards prediction"),
    ("deephit", "DeepHit: A Deep Learning Approach to Survival Analysis with Competing Risks", 2018, "Changhee Lee; William Zame; Jinsung Yoon; Mihaela van der Schaar", "https://ojs.aaai.org/index.php/AAAI/article/view/11842", "primary_paper", "competing-risk neural survival distributions"),
    ("mtlr", "Learning patient-specific cancer survival distributions as a sequence of dependent regressors", 2011, "Chun-Nam Yu; Russell Greiner; Hsiu-Chin Lin; Vickie Baracos", "https://proceedings.neurips.cc/paper/2011/hash/2a38a4a9316c49e5a833517c45d31070-Abstract.html", "primary_paper", "multi-task logistic survival regression"),
    ("joint_models", "Joint modelling of longitudinal measurements and event time data", 1997, "Atsushi Tsiatis; Marie Davidian", "https://doi.org/10.1002/sim.4780160410", "primary_paper", "joint longitudinal-survival modeling"),
    ("gee", "Longitudinal Data Analysis Using Generalized Linear Models", 1986, "Kung-Yee Liang; Scott Zeger", "https://doi.org/10.1093/biomet/73.1.13", "primary_paper", "population-average longitudinal estimation"),
    ("mixed_models", "Maximum likelihood estimation of mixed effects models", 1982, "Nan Laird; James Ware", "https://doi.org/10.2307/2529876", "primary_paper", "random-effects longitudinal models"),
    # Forecasting and time series.
    ("forecasting_fpp3", "Forecasting: Principles and Practice", 2021, "Rob Hyndman; George Athanasopoulos", "https://otexts.com/fpp3/", "primary_book", "forecast workflow, evaluation and reconciliation"),
    ("ets_state_space", "Forecasting with Exponential Smoothing: The State Space Approach", 2008, "Rob Hyndman; Anne Koehler; Keith Ord; Ralph Snyder", "https://doi.org/10.1007/978-3-540-71918-2", "primary_book", "ETS state-space models"),
    ("theta", "The theta model: a decomposition approach to forecasting", 2000, "Vassilis Assimakopoulos; Konstantinos Nikolopoulos", "https://doi.org/10.1016/S0169-2070(00)00066-2", "primary_paper", "theta forecasting method"),
    ("croston", "Forecasting and stock control for intermittent demands", 1972, "John Croston", "https://doi.org/10.1057/jors.1972.50", "primary_paper", "intermittent-demand forecasting"),
    ("prophet", "Forecasting at Scale", 2018, "Sean Taylor; Benjamin Letham", "https://doi.org/10.1080/00031305.2017.1380080", "primary_paper", "decomposable trend-seasonality-holiday forecasts"),
    ("deep_ar", "DeepAR: Probabilistic Forecasting with Autoregressive Recurrent Networks", 2020, "David Salinas; Valentin Flunkert; Jan Gasthaus", "https://doi.org/10.1016/j.ijforecast.2019.07.001", "primary_paper", "global probabilistic recurrent forecasting"),
    ("nbeats", "N-BEATS: Neural basis expansion analysis for interpretable time series forecasting", 2020, "Boris Oreshkin; Dmitri Carpov; Nicolas Chapados; Yoshua Bengio", "https://openreview.net/forum?id=r1ecqn4YwB", "primary_paper", "basis-expansion neural forecasting"),
    ("nhits", "N-HiTS: Neural Hierarchical Interpolation for Time Series Forecasting", 2022, "Cristian Challu; Kin G. Olivares; Boris Oreshkin; Federico Garza; Max Mergenthaler-Canseco; Artur Dubrawski", "https://ojs.aaai.org/index.php/AAAI/article/view/25854", "primary_paper", "multirate hierarchical neural forecasting"),
    ("tft", "Temporal Fusion Transformers for Interpretable Multi-horizon Time Series Forecasting", 2021, "Bryan Lim; Sercan Arik; Nicolas Loeff; Tomas Pfister", "https://doi.org/10.1016/j.ijforecast.2021.03.012", "primary_paper", "multi-horizon attention forecasting architecture"),
    ("patchtst", "A Time Series is Worth 64 Words: Long-term Forecasting with Transformers", 2023, "Yuqi Nie; Nam Nguyen; Phanwadee Sinthong; Jayant Kalagnanam", "https://openreview.net/forum?id=Jbdc0vTOcol", "primary_paper", "patch-based channel-independent forecasting"),
    ("timesnet", "TimesNet: Temporal 2D-Variation Modeling for General Time Series Analysis", 2023, "Haixu Wu; Tengge Hu; Yong Liu; Hang Zhou; Jianmin Wang; Mingsheng Long", "https://openreview.net/forum?id=ju_Uqw384Oq", "primary_paper", "period-aware time-series representation"),
    ("garch", "Generalized Autoregressive Conditional Heteroskedasticity", 1986, "Tim Bollerslev", "https://doi.org/10.1016/0304-4076(86)90063-1", "primary_paper", "conditional variance forecasting"),
    ("forecast_reconciliation", "Optimal combination forecasts for hierarchical time series", 2011, "Rob Hyndman; Roman Ahmed; George Athanasopoulos; Han Lin Shang", "https://doi.org/10.1016/j.csda.2011.03.006", "primary_paper", "coherent hierarchical forecast reconciliation"),
    # Anomaly, novelty, change and online adaptation.
    ("isolation_forest", "Isolation Forest", 2008, "Fei Tony Liu; Kai Ming Ting; Zhi-Hua Zhou", "https://doi.org/10.1109/ICDM.2008.17", "primary_paper", "random partition anomaly scoring"),
    ("lof", "LOF: Identifying Density-Based Local Outliers", 2000, "Markus Breunig; Hans-Peter Kriegel; Raymond Ng; Joerg Sander", "https://doi.org/10.1145/342009.335388", "primary_paper", "local density anomaly scoring"),
    ("one_class_svm", "Estimating the Support of a High-Dimensional Distribution", 2001, "Bernhard Schoelkopf; John Platt; John Shawe-Taylor; Alex Smola; Robert Williamson", "https://doi.org/10.1162/089976601750264965", "primary_paper", "one-class support estimation"),
    ("matrix_profile", "Matrix Profile I", 2016, "Chin-Chia Michael Yeh; Yan Zhu; Liudmila Ulanova; Nurjahan Begum; Yifei Ding; Hoang Anh Dau; Diego Silva; Abdullah Mueen; Eamonn Keogh", "https://doi.org/10.1109/ICDM.2016.0179", "primary_paper", "exact subsequence similarity profile"),
    ("pelt", "Optimal Detection of Changepoints With a Linear Computational Cost", 2012, "Rebecca Killick; Paul Fearnhead; Idris Eckley", "https://doi.org/10.1080/01621459.2012.737745", "primary_paper", "pruned exact changepoint segmentation"),
    ("bocpd", "Bayesian Online Changepoint Detection", 2007, "Ryan Adams; David MacKay", "https://arxiv.org/abs/0710.3742", "primary_paper", "online run-length posterior change detection"),
    ("adwin", "Learning from Time-Changing Data with Adaptive Windowing", 2007, "Albert Bifet; Ricard Gavalda", "https://doi.org/10.1137/1.9781611972771.42", "primary_paper", "adaptive-window drift detection"),
    ("hoeffding_tree", "Mining High-Speed Data Streams", 2000, "Pedro Domingos; Geoff Hulten", "https://doi.org/10.1145/347090.347107", "primary_paper", "incremental Hoeffding decision trees"),
    ("adaptive_rf", "Adaptive Random Forests for Evolving Data Stream Classification", 2017, "Heitor Gomes; Albert Bifet; Jesse Read; Jean Paul Barddal; Fabrice Enembreck; Bernhard Pfahringer; Geoff Holmes; Talel Abdessalem", "https://doi.org/10.1007/s10994-017-5642-8", "primary_paper", "drift-aware streaming tree ensemble"),
    # Conformal prediction and uncertainty.
    ("conformal_book", "Algorithmic Learning in a Random World", 2005, "Vladimir Vovk; Alexander Gammerman; Glenn Shafer", "https://link.springer.com/book/10.1007/b106715", "primary_book", "conformal prediction foundations"),
    ("split_conformal", "A Distribution-Free Predictive Inference for Regression", 2018, "Jing Lei; Max G'Sell; Alessandro Rinaldo; Ryan Tibshirani; Larry Wasserman", "https://doi.org/10.1080/01621459.2017.1307116", "primary_paper", "split conformal regression intervals"),
    ("jackknife_plus", "Predictive inference with the jackknife+", 2021, "Rina Barber; Emmanuel Candes; Aaditya Ramdas; Ryan Tibshirani", "https://doi.org/10.1214/20-AOS1965", "primary_paper", "jackknife+ predictive intervals"),
    ("conformal_classification", "Uncertainty Sets for Image Classifiers using Conformal Prediction", 2021, "Anastasios Angelopoulos; Stephen Bates; Jitendra Malik; Michael Jordan", "https://openreview.net/forum?id=eNdiU_DbM9", "primary_paper", "adaptive prediction sets"),
    ("label_shift_cp", "Distribution-free uncertainty quantification for classification under label shift", 2021, "Aleksandr Podkopaev; Aaditya Ramdas", "https://proceedings.mlr.press/v161/podkopaev21a.html", "primary_paper", "label-shift-aware conformal and calibration"),
    ("modular_conformal", "Modular Conformal Calibration", 2022, "Charles Marx; Shengjia Zhao; Willie Neiswanger; Stefano Ermon", "https://proceedings.mlr.press/v162/marx22a.html", "primary_paper", "regression distribution recalibration"),
    ("risk_controlling", "Learn then Test: Calibrating Predictive Algorithms to Achieve Risk Control", 2022, "Anastasios Angelopoulos; Stephen Bates; Emmanuel Candes; Michael Jordan", "https://arxiv.org/abs/2110.01052", "primary_paper", "finite-sample risk-controlling prediction"),
    # Graph predictive analytics.
    ("deepwalk", "DeepWalk: Online Learning of Social Representations", 2014, "Bryan Perozzi; Rami Al-Rfou; Steven Skiena", "https://doi.org/10.1145/2623330.2623732", "primary_paper", "random-walk graph embeddings"),
    ("node2vec", "node2vec: Scalable Feature Learning for Networks", 2016, "Aditya Grover; Jure Leskovec", "https://doi.org/10.1145/2939672.2939754", "primary_paper", "biased random-walk graph embeddings"),
    ("gcn", "Semi-Supervised Classification with Graph Convolutional Networks", 2017, "Thomas Kipf; Max Welling", "https://openreview.net/forum?id=SJU4ayYgl", "primary_paper", "spectral graph convolution for node prediction"),
    ("graphsage", "Inductive Representation Learning on Large Graphs", 2017, "William Hamilton; Rex Ying; Jure Leskovec", "https://proceedings.neurips.cc/paper/2017/hash/5dd9db5e033da9c6fb5ba83c7a7ebea9-Abstract.html", "primary_paper", "sample-and-aggregate inductive graph prediction"),
    ("gat", "Graph Attention Networks", 2018, "Petar Velickovic; Guillem Cucurull; Arantxa Casanova; Adriana Romero; Pietro Lio; Yoshua Bengio", "https://openreview.net/forum?id=rJXMpikCZ", "primary_paper", "attention-weighted neighborhood aggregation"),
    ("rgcn", "Modeling Relational Data with Graph Convolutional Networks", 2018, "Michael Schlichtkrull; Thomas Kipf; Peter Bloem; Rianne van den Berg; Ivan Titov; Max Welling", "https://arxiv.org/abs/1703.06103", "primary_paper", "typed-relation graph convolution"),
    ("tgn", "Temporal Graph Networks for Deep Learning on Dynamic Graphs", 2020, "Emanuele Rossi; Ben Chamberlain; Fabrizio Frasca; Davide Eynard; Federico Monti; Michael Bronstein", "https://arxiv.org/abs/2006.10637", "primary_paper", "memory-based temporal graph prediction"),
    ("tgat", "Inductive Representation Learning on Temporal Graphs", 2020, "Da Xu; Chuanwei Ruan; Evren Korpeoglu; Sushant Kumar; Kannan Achan", "https://openreview.net/forum?id=rJeW1yHYwH", "primary_paper", "time-encoding temporal graph attention"),
    ("hetero_graph_transformer", "Heterogeneous Graph Transformer", 2020, "Ziniu Hu; Yuxiao Dong; Kuansan Wang; Yizhou Sun", "https://doi.org/10.1145/3366423.3380027", "primary_paper", "typed-node and typed-edge attention prediction"),
    # Causal prediction and uplift; identification remains separate.
    ("causal_forest", "Generalized Random Forests", 2019, "Susan Athey; Julie Tibshirani; Stefan Wager", "https://doi.org/10.1214/18-AOS1709", "primary_paper", "forest-based conditional effect estimation"),
    ("xlearner", "Metalearners for estimating heterogeneous treatment effects", 2019, "Soren Kunzel; Jasjeet Sekhon; Peter Bickel; Bin Yu", "https://doi.org/10.1073/pnas.1804597116", "primary_paper", "S/T/X learner effect estimation"),
    ("rlearner", "Quasi-Oracle Estimation of Heterogeneous Treatment Effects", 2019, "Xinkun Nie; Stefan Wager", "https://arxiv.org/abs/1712.04912", "primary_paper", "residualized R-learner objective"),
    ("drlearner", "Towards Optimal Doubly Robust Estimation of Heterogeneous Causal Effects", 2020, "Edward Kennedy", "https://arxiv.org/abs/2004.14497", "primary_paper", "doubly robust pseudo-outcome learner"),
    ("uplift_tree", "True Lift Model", 2012, "Nicholas Radcliffe; Patrick Surry", "https://stochasticsolutions.com/pdf/true_lift.pdf", "primary_paper", "uplift segmentation"),
    ("causalml_docs", "CausalML documentation", 2026, "CausalML contributors", "https://causalml.readthedocs.io/en/latest/", "official_reference", "uplift and heterogeneous-effect implementation"),
    ("dowhy_docs", "DoWhy documentation", 2026, "PyWhy contributors", "https://www.pywhy.org/dowhy/", "official_reference", "causal graph, identification, estimation and refutation"),
    ("econml_docs", "EconML documentation", 2026, "EconML contributors", "https://econml.azurewebsites.net/", "official_reference", "orthogonal and heterogeneous treatment-effect estimators"),
    # Weak/semi/self-supervision, missingness and representation learning.
    ("label_model", "Data Programming: Creating Large Training Sets, Quickly", 2017, "Alexander Ratner; Stephen Bach; Henry Ehrenberg; Jason Fries; Sen Wu; Christopher Re", "https://proceedings.neurips.cc/paper/2016/hash/6709e8d64a5f47269ed5cea9f625f7ab-Abstract.html", "primary_paper", "weak-supervision label model"),
    ("positive_unlabeled", "Learning Classifiers from Only Positive and Unlabeled Data", 2008, "Charles Elkan; Keith Noto", "https://doi.org/10.1145/1401890.1401920", "primary_paper", "positive-unlabeled risk correction"),
    ("label_propagation", "Learning with Local and Global Consistency", 2004, "Dengyong Zhou; Olivier Bousquet; Thomas Lal; Jason Weston; Bernhard Schoelkopf", "https://proceedings.neurips.cc/paper/2003/hash/87682805257e619d49b8e0dfdc14affa-Abstract.html", "primary_paper", "graph label propagation"),
    ("cotrain", "Combining labeled and unlabeled data with co-training", 1998, "Avrim Blum; Tom Mitchell", "https://doi.org/10.1145/279943.279962", "primary_paper", "multi-view co-training"),
    ("simclr", "A Simple Framework for Contrastive Learning of Visual Representations", 2020, "Ting Chen; Simon Kornblith; Mohammad Norouzi; Geoffrey Hinton", "https://proceedings.mlr.press/v119/chen20j.html", "primary_paper", "contrastive non-generative representation learning"),
    ("byol", "Bootstrap Your Own Latent", 2020, "Jean-Bastien Grill; Florian Strub; Florent Altche; Corentin Tallec; Pierre Richemond; Elena Buchatskaya; Carl Doersch; Bernardo Avila Pires; Zhaohan Guo; Mohammad Gheshlaghi Azar; Bilal Piot; Koray Kavukcuoglu; Remi Munos; Michal Valko", "https://proceedings.neurips.cc/paper/2020/hash/f3ada80d5c4ee70142b17b8192b2958e-Abstract.html", "primary_paper", "self-distillation representation learning"),
    ("dino", "Emerging Properties in Self-Supervised Vision Transformers", 2021, "Mathilde Caron; Hugo Touvron; Ishan Misra; Herve Jegou; Julien Mairal; Piotr Bojanowski; Armand Joulin", "https://openaccess.thecvf.com/content/ICCV2021/html/Caron_Emerging_Properties_in_Self-Supervised_Vision_Transformers_ICCV_2021_paper.html", "primary_paper", "self-supervised vision representation learning"),
    ("mice", "Multiple Imputation by Chained Equations", 2011, "Stef van Buuren; Karin Groothuis-Oudshoorn", "https://doi.org/10.18637/jss.v045.i03", "primary_paper", "chained-equation multiple imputation"),
    ("missforest", "MissForest—non-parametric missing value imputation", 2012, "Daniel Stekhoven; Peter Buehlmann", "https://doi.org/10.1093/bioinformatics/btr597", "primary_paper", "random-forest mixed-type imputation"),
    # Interpretability, rules, fairness and safety.
    ("lime", "Why Should I Trust You? Explaining the Predictions of Any Classifier", 2016, "Marco Ribeiro; Sameer Singh; Carlos Guestrin", "https://doi.org/10.1145/2939672.2939778", "primary_paper", "local surrogate explanations"),
    ("shap", "A Unified Approach to Interpreting Model Predictions", 2017, "Scott Lundberg; Su-In Lee", "https://proceedings.neurips.cc/paper/2017/hash/8a20a8621978632d76c43dfd28b67767-Abstract.html", "primary_paper", "Shapley-attribution explanations"),
    ("anchor", "Anchors: High-Precision Model-Agnostic Explanations", 2018, "Marco Ribeiro; Sameer Singh; Carlos Guestrin", "https://ojs.aaai.org/index.php/AAAI/article/view/11491", "primary_paper", "local sufficient rule explanations"),
    ("rulefit", "Predictive Learning via Rule Ensembles", 2008, "Jerome Friedman; Bogdan Popescu", "https://doi.org/10.1214/07-AOAS148", "primary_paper", "sparse rule ensemble"),
    ("ebm", "InterpretML: A Unified Framework for Machine Learning Interpretability", 2019, "Harsha Nori; Samuel Jenkins; Paul Koch; Rich Caruana", "https://arxiv.org/abs/1909.09223", "primary_paper", "explainable boosting machines and interpretation tooling"),
    ("fair_reductions", "A Reductions Approach to Fair Classification", 2018, "Alekh Agarwal; Alina Beygelzimer; Miroslav Dudik; John Langford; Hanna Wallach", "https://proceedings.mlr.press/v80/agarwal18a.html", "primary_paper", "constraint-based group-fair classification"),
    ("equalized_odds", "Equality of Opportunity in Supervised Learning", 2016, "Moritz Hardt; Eric Price; Nathan Srebro", "https://proceedings.neurips.cc/paper/2016/hash/9d2682367c3935defcb1f9e247a97c0d-Abstract.html", "primary_paper", "equalized-odds postprocessing"),
    # Process prediction, state-aware OCEL, temporal EKG and exact user-requested artifacts.
    ("process_predictive_survey", "Predictive Business Process Monitoring with LSTM Neural Networks", 2017, "Niek Tax; Ilya Verenich; Marcello La Rosa; Marlon Dumas", "https://doi.org/10.1007/978-3-319-59536-8_26", "primary_paper", "next-event, time and outcome prediction from traces"),
    ("ocppa", "Object-centric Process Predictive Analytics", 2022, "Riccardo Galanti; Massimiliano de Leoni; Nicolo Navarin; Alan Marazzi", "https://arxiv.org/abs/2203.02801", "primary_paper", "interaction-aware object-centric process prediction"),
    ("hoeg", "HOEG: A New Approach for Object-Centric Predictive Process Monitoring", 2024, "Tim K. Smit; Hajo A. Reijers; Xixi Lu", "https://arxiv.org/abs/2404.05316", "primary_paper", "heterogeneous object-event graph encoding plus GNN prediction"),
    ("tekg", "Transforming Object-Centric Event Logs to Temporal Event Knowledge Graphs", 2024, "Shahrzad Khayatbashi; Olaf Hartig; Amin Jalali", "https://arxiv.org/abs/2406.07596", "primary_paper", "snapshot-preserving OCEL-to-temporal-EKG transformation"),
    ("sa_ocpm", "State-Aware Object-Centric Process Mining: Enhancing OCEL 2.0 with Explicit State Transitions", 2025, "Dina Kretzschmann; Alessandro Berti; Wil van der Aalst", "https://www.alessandroberti.it/new_papers/2025_Dina_SAOCPM.pdf", "primary_paper", "derived state transitions and state-aware event projection"),
    ("oced_core", "Towards a Simple and Extensible Standard for Object-Centric Event Data", 2024, "Dirk Fahland; Marco Montali; Julian Lebherz; Wil van der Aalst", "https://arxiv.org/abs/2410.14495", "primary_paper", "OCED core model, design space and limits"),
    ("ekg_fahland", "Process mining over multiple behavioral dimensions with event knowledge graphs", 2022, "Dirk Fahland", "https://doi.org/10.1007/s12525-021-00510-6", "primary_paper", "event knowledge graph process representation"),
    ("docel", "Enhancing Data-Awareness of Object-Centric Event Logs", 2023, "Xixi Lu; Alessandro Berti; Felix Mannhardt; Wil van der Aalst", "https://arxiv.org/abs/2212.02858", "primary_paper", "data-aware OCEL and dynamic attribute linkage"),
    ("cases_ocel", "Defining Cases and Variants for Object-Centric Event Data", 2022, "Jan Niklas Adams; Daniel Schuster; Wil van der Aalst", "https://arxiv.org/abs/2208.03235", "primary_paper", "case and variant projection from object-centric graphs"),
    ("concept_drift_actor", "Multi-perspective Concept Drift Detection: Including the Actor Perspective", 2024, "Eva Klijn; Felix Mannhardt; Dirk Fahland", "https://research.tue.nl/en/publications/multi-perspective-concept-drift-detection-including-the-actor-per", "primary_paper", "actor-aware process drift detection"),
    # Spatial, text, image and signal prediction.
    ("kriging", "A Statistical Approach to Some Basic Mine Valuation Problems", 1951, "Danie Krige", "https://doi.org/10.10520/AJA0038223X_4792", "primary_paper", "geostatistical spatial prediction"),
    ("gwr", "Geographically Weighted Regression", 1996, "Chris Brunsdon; Stewart Fotheringham; Martin Charlton", "https://doi.org/10.1111/j.1538-4632.1996.tb00936.x", "primary_paper", "location-varying regression"),
    ("hawkes", "Spectra of Some Self-Exciting and Mutually Exciting Point Processes", 1971, "Alan Hawkes", "https://doi.org/10.1093/biomet/58.1.83", "primary_paper", "self-exciting event intensity"),
    ("crf", "Conditional Random Fields", 2001, "John Lafferty; Andrew McCallum; Fernando Pereira", "https://repository.upenn.edu/cis_papers/159/", "primary_paper", "discriminative structured sequence prediction"),
    ("hmm", "A Tutorial on Hidden Markov Models", 1989, "Lawrence Rabiner", "https://doi.org/10.1109/5.18626", "primary_paper", "hidden-state sequence prediction"),
    ("resnet", "Deep Residual Learning for Image Recognition", 2016, "Kaiming He; Xiangyu Zhang; Shaoqing Ren; Jian Sun", "https://openaccess.thecvf.com/content_cvpr_2016/html/He_Deep_Residual_Learning_CVPR_2016_paper.html", "primary_paper", "residual convolutional predictive architecture"),
    ("vit", "An Image is Worth 16x16 Words", 2021, "Alexey Dosovitskiy; Lucas Beyer; Alexander Kolesnikov; Dirk Weissenborn; Xiaohua Zhai; Thomas Unterthiner; Mostafa Dehghani; Matthias Minderer; Georg Heigold; Sylvain Gelly; Jakob Uszkoreit; Neil Houlsby", "https://openreview.net/forum?id=YicbFdNTTy", "primary_paper", "vision transformer predictive architecture"),
    ("hog", "Histograms of Oriented Gradients for Human Detection", 2005, "Navneet Dalal; Bill Triggs", "https://doi.org/10.1109/CVPR.2005.177", "primary_paper", "classical image feature extraction"),
    ("tfidf", "A Statistical Interpretation of Term Specificity and Its Application in Retrieval", 1972, "Karen Sparck Jones", "https://doi.org/10.1108/eb026526", "primary_paper", "inverse document frequency weighting"),
    # Recent non-generative predictive innovations and evaluation caveats.
    ("tabpfn", "TabPFN: A Transformer That Solves Small Tabular Classification Problems in a Second", 2022, "Noah Hollmann; Samuel Mueller; Katharina Eggensperger; Frank Hutter", "https://openreview.net/forum?id=eu9fVjVasr4", "primary_paper", "prior-data-fitted tabular classification; task-size assumptions limit scope"),
    ("tabtransformer", "TabTransformer: Tabular Data Modeling Using Contextual Embeddings", 2021, "Xin Huang; Ashish Khetan; Milan Cvitkovic; Zohar Karnin", "https://arxiv.org/abs/2012.06678", "primary_paper", "attention-based categorical tabular prediction"),
    ("ft_transformer", "Revisiting Deep Learning Models for Tabular Data", 2021, "Yury Gorishniy; Ivan Rubachev; Valentin Khrulkov; Artem Babenko", "https://proceedings.neurips.cc/paper/2021/hash/9d86d83f925f2149e9edb0ac3b49229c-Abstract.html", "primary_paper", "strong tabular neural baselines and FT-Transformer"),
    ("dream", "Distributionally Robust Evaluation of Machine Learning Models", 2023, "research contributors", "https://proceedings.mlr.press/v206/", "conference_proceedings", "recent distribution-shift and predictive evaluation research index"),
    ("forecasting_conformal", "Conformal Prediction for Time Series", 2023, "Victor Chernozhukov; Kaspar Wuthrich; Yinchu Zhu", "https://arxiv.org/abs/1802.06300", "primary_paper", "block and dependence-aware conformal time-series inference"),
    ("selective_classification", "SelectiveNet: A Deep Neural Network with an Integrated Reject Option", 2019, "Yonatan Geifman; Ran El-Yaniv", "https://proceedings.mlr.press/v97/geifman19a.html", "primary_paper", "coverage-risk selective prediction"),
    ("deep_ensembles", "Simple and Scalable Predictive Uncertainty Estimation using Deep Ensembles", 2017, "Balaji Lakshminarayanan; Alexander Pritzel; Charles Blundell", "https://proceedings.neurips.cc/paper/2017/hash/9ef2ed4b7fd2c810847ffa5fa85bce38-Abstract.html", "primary_paper", "ensemble-based neural predictive uncertainty"),
    ("tabnet", "TabNet: Attentive Interpretable Tabular Learning", 2021, "Sercan Arik; Tomas Pfister", "https://ojs.aaai.org/index.php/AAAI/article/view/16826", "primary_paper", "sequential attention for tabular prediction"),
    ("saint", "SAINT: Improved Neural Networks for Tabular Data via Row Attention and Contrastive Pre-Training", 2021, "Gowthami Somepalli; Micah Goldblum; Avi Schwarzschild; C Bayan Bruss; Tom Goldstein", "https://arxiv.org/abs/2106.01342", "primary_paper", "row/column attention and contrastive tabular pretraining"),
    ("autoformer", "Autoformer: Decomposition Transformers with Auto-Correlation for Long-Term Series Forecasting", 2021, "Haixu Wu; Jiehui Xu; Jianmin Wang; Mingsheng Long", "https://proceedings.neurips.cc/paper/2021/hash/bcc0d400288793e8bdcd7c19a8ac0c2b-Abstract.html", "primary_paper", "decomposition and autocorrelation forecasting architecture"),
    ("fedformer", "FEDformer: Frequency Enhanced Decomposed Transformer for Long-term Series Forecasting", 2022, "Tian Zhou; Ziqing Ma; Qingsong Wen; Xue Wang; Liang Sun; Rong Jin", "https://proceedings.mlr.press/v162/zhou22g.html", "primary_paper", "frequency-enhanced decomposed forecasting architecture"),
    ("dlinear", "Are Transformers Effective for Time Series Forecasting?", 2023, "Ailing Zeng; Muxi Chen; Lei Zhang; Qiang Xu", "https://ojs.aaai.org/index.php/AAAI/article/view/26317", "primary_paper", "decomposition-linear forecasting and benchmark critique"),
    ("tide", "Long-term Forecasting with TiDE: Time-series Dense Encoder", 2023, "Abhimanyu Das; Weihao Kong; Andrew Leach; Rajat Sen; Rose Yu; Yichen Zhou", "https://arxiv.org/abs/2304.08424", "primary_paper", "dense encoder-decoder multi-horizon forecasting"),
    ("tsmixer", "TSMixer: An All-MLP Architecture for Time Series Forecasting", 2023, "Vijay Ekambaram; Arindam Jati; Nam Nguyen; Pankaj Dayama; Chandra Reddy; Wesley Gifford; Jayant Kalagnanam", "https://arxiv.org/abs/2303.06053", "primary_paper", "time/feature mixing MLP forecasting"),
    ("itransformer", "iTransformer: Inverted Transformers Are Effective for Time Series Forecasting", 2024, "Yong Liu; Tengge Hu; Haoran Zhang; Haixu Wu; Shiyu Wang; Lintao Ma; Mingsheng Long", "https://openreview.net/forum?id=JePfAI8fah", "primary_paper", "variate-token inverted forecasting architecture"),
    ("timemixer", "TimeMixer: Decomposable Multiscale Mixing for Time Series Forecasting", 2024, "Shiyu Wang; Haixu Wu; Xiaoming Shi; Tengge Hu; Huakun Luo; Lintao Ma; James Y Zhang; Jun Zhou", "https://openreview.net/forum?id=7oLshfEIC2", "primary_paper", "multiscale past/future mixing forecast architecture"),
    ("tabr", "TabR: Tabular Deep Learning Meets Nearest Neighbors", 2024, "Yury Gorishniy; Ivan Rubachev; Nikolay Kartashev; Daniil Shlenskii; Akim Kotelnikov; Artem Babenko", "https://arxiv.org/abs/2307.14338", "primary_paper", "retrieval-augmented discriminative tabular predictor; not RAG/LLM semantics"),
    ("modernnca", "Revisiting Nearest Neighbor for Tabular Data: A Deep Tabular Baseline Two Decades Later", 2024, "Jintai Chen; Jiahuan Yan; Qianhui Wang; Huimin Wu; Xinggang Wang; Yicheng Gao", "https://arxiv.org/abs/2407.03257", "primary_paper", "learned-neighborhood tabular classification and regression"),
    ("realmlp", "Better by Default: Strong Pre-Tuned MLPs and Boosted Trees on Tabular Data", 2024, "David Holzmuller; Leo Grinsztajn; Ingo Steinwart", "https://arxiv.org/abs/2407.04491", "primary_paper", "pre-tuned tabular predictive baselines"),
    ("graphgps", "Recipe for a General, Powerful, Scalable Graph Transformer", 2022, "Ladislav Rampasek; Michael Galkin; Vijay Prakash Dwivedi; Anh Tuan Luu; Guy Wolf; Dominique Beaini", "https://arxiv.org/abs/2205.12454", "primary_paper", "local message passing plus global attention graph prediction"),
    ("graphmae", "GraphMAE: Self-Supervised Masked Graph Autoencoders", 2022, "Zhenyu Hou; Xiao Liu; Yukuo Cen; Yuxiao Dong; Hongxia Yang; Chunjie Wang; Jie Tang", "https://arxiv.org/abs/2205.10803", "primary_paper", "masked-feature graph representation learning"),
    ("dygformer", "DyGFormer: A Transformer-based Architecture for Dynamic Graph Learning", 2023, "Le Yu; Leilei Sun; Bowen Du; Weifeng Lv", "https://arxiv.org/abs/2303.13047", "primary_paper", "historical interaction sequence encoding for dynamic graph prediction"),
    ("tgb", "Towards Better Evaluation for Dynamic Link Prediction", 2023, "Shenyang Huang; Farimah Poursafaei; Jacob Danovitch; Matthias Fey; Weihua Hu; Emanuele Rossi; Jure Leskovec; Michael Bronstein; Kimon Fountoulakis; Ismail Ceylan", "https://arxiv.org/abs/2307.01026", "primary_paper", "temporal graph benchmark, negative sampling and evaluation protocols"),
    ("anomaly_transformer", "Anomaly Transformer: Time Series Anomaly Detection with Association Discrepancy", 2022, "Jiehui Xu; Haixu Wu; Jianmin Wang; Mingsheng Long", "https://openreview.net/forum?id=LzQQ89U1qm_", "primary_paper", "association-discrepancy time-series anomaly scoring"),
    ("tranad", "TranAD: Deep Transformer Networks for Anomaly Detection in Multivariate Time Series Data", 2022, "Shreshth Tuli; Giuliano Casale; Nicholas Jennings", "https://arxiv.org/abs/2201.07284", "primary_paper", "multivariate time-series anomaly reconstruction/scoring"),
    ("dcdetector", "DCdetector: Dual Attention Contrastive Representation Learning for Time Series Anomaly Detection", 2023, "Yiyuan Yang; Chaoli Zhang; Tian Zhou; Qingsong Wen; Liang Sun", "https://arxiv.org/abs/2306.10347", "primary_paper", "contrastive dual-attention anomaly scoring"),
    ("survtrace", "SurvTRACE: Transformers for Survival Analysis with Competing Events", 2022, "Zifeng Wang; Jimeng Sun", "https://arxiv.org/abs/2110.00855", "primary_paper", "competing-event neural survival prediction"),
    ("conformal_risk_control", "Conformal Risk Control", 2024, "Anastasios Angelopoulos; Stephen Bates; Adam Fisch; Lihua Lei; Tal Schuster", "https://openreview.net/forum?id=33XGfHLtZg", "primary_paper", "distribution-free control of monotone predictive risk"),
]


def parse_authors(text: str) -> list[str]:
    if any(x in text.lower() for x in ("maintainer", "contributors", "working group", "team", "authors", "core team", "consortium")):
        return []
    return [x.strip() for x in text.split(";") if x.strip()]


SOURCES = []
for key, title, year, authors, url, kind, scope in SOURCE_SPECS:
    SOURCES.append({
        "source_id": f"source.predictive.{key}", "edition": EDITION, "title": title,
        "year": year, "authors_or_publisher": authors, "authors": parse_authors(authors),
        "url": url, "kind": kind, "primary_or_official": True,
        "authority_scope": scope,
        "retrieval_status": "opened_and_checked" if key in {"hoeg", "tekg", "sa_ocpm", "oced_core", "ocppa", "ocel20", "label_shift_cp", "modular_conformal"} else "curated_primary_reference",
        "limitations": "Authority is limited to the named artifact and evaluated conditions; citation, benchmark rank, or provider documentation does not establish universal superiority or deployment conformance.",
        "accessed_at": ACCESSED,
    })


GROUP_CONTRACTS = {
    "regression": ("numeric outcome or conditional functional", "row/table or sparse design matrix", "authorized sampling and stable feature/label meaning", "minimize declared regression loss plus regularization", "point/distribution/interval prediction"),
    "classification": ("binary, multiclass, multilabel or ordinal label", "row/table, sparse vectors or learned representation", "class ontology and label observation process are explicit", "minimize proper, margin or cost-sensitive classification objective", "class, score, probability or prediction set"),
    "count_compositional": ("count, rate, proportion, bounded or compositional outcome", "exposure-qualified observations", "support, link, exposure and zero process are explicit", "maximize declared likelihood or minimize proper deviance", "support-valid conditional prediction"),
    "tree_ensemble": ("numeric, categorical, survival or uplift target", "mixed-type feature table with declared missing/categorical semantics", "partition stability and training/inference category rules are explicit", "fit recursive partitions or boosted additive trees", "tree-ensemble prediction plus structure receipt"),
    "kernel_margin": ("class, score, numeric response or support boundary", "finite feature vectors plus kernel contract", "kernel is positive semidefinite where required and scaling is fixed", "optimize regularized margin or kernel likelihood", "score, class, response or uncertainty"),
    "probabilistic_bayesian": ("posterior or posterior-predictive quantity", "typed observations and prior/model graph", "likelihood, prior, exchangeability and identifiability assumptions are explicit", "sample or approximate the declared posterior", "posterior predictive distribution plus diagnostics"),
    "calibration_ensemble": ("calibrated probability, prediction set or ensemble output", "base predictions plus disjoint calibration/meta-training observations", "calibration exchangeability and out-of-fold provenance are explicit", "optimize proper score, calibration loss or ensemble risk", "calibrated/combined prediction with provenance"),
    "ranking": ("ordered items for a query/context", "query-item judgments, interactions or pair/list preferences", "position bias, censoring and candidate universe are explicit", "optimize pointwise, pairwise or listwise ranking objective", "scored and deterministically tied ranking"),
    "recommendation": ("item relevance, utility or next-choice outcome", "user/item/context interactions with exposure semantics", "missing interaction is not silently treated as dislike", "optimize explicit/implicit feedback objective", "ranked recommendation with candidate and policy provenance"),
    "survival_event_history": ("time-to-event, hazard, incidence or competing-risk outcome", "start/stop/event/censoring observations", "time origin, censoring, truncation and competing events are explicit", "maximize survival likelihood or minimize censored risk", "survival/hazard/incidence distribution"),
    "longitudinal_panel": ("within/between-entity response trajectory", "entity-indexed repeated observations", "dependence, random effects, attrition and observation schedule are explicit", "fit marginal, conditional or latent trajectory model", "entity/population trajectory prediction"),
    "forecasting": ("future value, distribution, interval or hierarchy", "ordered series with origin, frequency and availability times", "temporal causality, horizon, revisions and future-known covariates are explicit", "minimize rolling-origin forecast loss or likelihood", "horizon-indexed forecast with origin"),
    "anomaly_change": ("novelty score, anomaly decision or change point", "reference and monitored observations", "normal/reference regime and contamination assumptions are explicit", "estimate support/density/residual/run-length or change statistic", "score/change posterior plus threshold decision"),
    "online_drift": ("stream prediction under possible drift", "ordered examples with event and label-availability times", "update order, delayed labels, recurrence and reset authority are explicit", "incrementally minimize predictive loss and/or detect drift", "prediction plus online-state transition receipt"),
    "graph": ("node, edge, subgraph or graph-level target", "typed graph snapshot or temporal graph", "node/edge identity, direction, multiplicity, sampling and time semantics are explicit", "optimize graph predictive objective", "graph-indexed prediction/embedding"),
    "process_prediction": ("next activity/time, remaining time, outcome, violation or risk", "case-centric trace or object-centric event graph", "event order, observation cutoff, case/object projection and state validity are explicit", "fit prefix/event-graph predictive objective", "process-state prediction with cutoff provenance"),
    "spatiotemporal": ("location/time-indexed response, intensity or event", "CRS-qualified features, raster, trajectory or point process", "CRS, support, neighborhood, spatial leakage and temporal cutoff are explicit", "fit spatial covariance, autoregression, intensity or graph objective", "location/time-qualified prediction"),
    "weak_semisupervised": ("label from limited, weak, positive-only or multi-view supervision", "labeled/unlabeled examples plus labeling-source graph", "label-source dependence, class prior and view assumptions are explicit", "fit label model, consistency, propagation or corrected risk", "prediction plus supervision provenance"),
    "missing_censoring": ("prediction under missing, censored or truncated observation", "values plus missingness/censoring indicators and observation process", "MCAR/MAR/MNAR or censoring assumptions are never inferred", "fit imputation, weighting, joint or sensitivity model", "completed/predicted values plus uncertainty and imputations"),
    "causal_uplift": ("conditional treatment effect or incremental response", "treatment, outcome, covariates and study assignment record", "identification is established outside the predictive learner", "fit nuisance and effect functions under declared orthogonal/uplift loss", "CATE/uplift prediction plus identification reference"),
    "interpretable_symbolic": ("prediction plus rule, shape or symbolic representation", "typed tabular or symbolic features", "interpretability audience and fidelity/stability metric are explicit", "fit sparse rule, additive shape, fuzzy or symbolic objective", "prediction plus bounded explanation artifact"),
    "text_sequence": ("document, token, sequence or structured-label target", "normalized text/tokens/sequences with language and segmentation contract", "tokenization, label alignment and domain shift are explicit", "fit discriminative sequence/text predictive objective", "class, span, tag or sequence prediction"),
    "image_signal": ("image, frame, waveform or spectral target", "coordinate/sampling-qualified tensors or extracted features", "sampling, units, calibration, augmentation and acquisition shift are explicit", "fit feature-based or neural discriminative objective", "class, score, localization or signal forecast"),
    "representation_selfsupervised": ("transfer representation for downstream prediction", "unlabeled paired/augmented views plus downstream split", "augmentation invariances and pretraining/downstream overlap are explicit", "optimize contrastive, redundancy-reduction or self-distillation objective", "versioned representation encoder; not a business prediction"),
}


TAXONOMY_AXES = {
    "axis_id": "taxonomy.predictive_ml.orthogonal_axes", "edition": EDITION,
    "anti_cross_product_law": "Axis values classify a resolved occurrence, not a Cartesian product of model names. Unknown and multiple values are first-class; no axis value implies another.",
    "axes": [
        {"name": "output_geometry", "values": ["scalar", "vector", "matrix", "ranked_list", "set", "interval", "sequence", "graph_indexed", "distribution", "survival_curve", "hazard", "event_intensity", "time_to_event", "spatial_field", "structured_labels"], "law": "Geometry does not imply statistical meaning or uncertainty."},
        {"name": "learning_signal", "values": ["fully_supervised", "weakly_supervised", "semi_supervised", "self_supervised_representation", "positive_unlabeled", "online_supervised", "multitask", "transfer", "active_learning"], "law": "Pretraining/label acquisition posture is separate from the downstream prediction task."},
        {"name": "data_generating_posture", "values": ["iid_claimed", "grouped", "clustered", "longitudinal", "panel", "time_ordered", "spatial", "spatiotemporal", "network_dependent", "event_process", "censored", "truncated", "competing_risk", "missing", "selected", "exposure_biased", "drifting", "intervention_affected"], "law": "IID is a proof obligation, never a default inferred from rows."},
        {"name": "epistemic_family", "values": ["parametric", "semiparametric", "nonparametric", "frequentist", "bayesian", "mechanistic", "statistical", "hybrid"], "law": "Parametric status and inferential school are independent axes."},
        {"name": "prediction_timing", "values": ["batch_retrospective", "batch_prospective", "rolling_origin", "event_triggered", "streaming_online", "real_time_request", "scheduled_refresh", "dynamic_landmark"], "law": "Training cadence, prediction cadence, horizon and label maturity are separate decisions."},
        {"name": "decision_proximity", "values": ["informational", "triage", "recommendation", "human_review_required", "decision_support", "automated_low_consequence", "automated_high_consequence_prohibited_without_policy"], "law": "A score does not authorize an action."},
        {"name": "target_kind", "values": ["continuous", "binary", "multiclass", "multilabel", "ordinal", "count", "rate", "proportion", "ranking", "recommendation", "time_to_event", "future_series", "anomaly", "change", "node", "edge", "graph", "next_event", "remaining_time", "treatment_effect", "spatial_response", "structured_sequence"], "law": "Business target and model output carrier remain distinct."},
        {"name": "uncertainty_form", "values": ["none_justified", "standard_error", "confidence_interval", "credible_interval", "prediction_interval", "prediction_set", "quantiles", "distribution", "ensemble_dispersion", "posterior", "conformal_risk_bound"], "law": "Uncertainty form does not imply calibrated coverage."},
        {"name": "update_posture", "values": ["immutable_fit", "scheduled_refit", "triggered_refit", "incremental", "continual", "sliding_window", "fading_memory", "state_resettable"], "law": "Online inference does not imply online learning."},
        {"name": "evaluation_posture", "values": ["random_holdout", "group_holdout", "out_of_time", "rolling_origin", "spatial_block", "external_site", "nested_cv", "progressive", "counterfactual_policy", "survival_censoring_aware"], "law": "A metric value is uninterpretable without its partition and observation policy."},
    ],
}


def axis_bindings(group: str, name: str) -> dict[str, list[str]]:
    geometry = {
        "classification": ["scalar", "vector", "set"], "ranking": ["ranked_list"], "recommendation": ["ranked_list"],
        "survival_event_history": ["survival_curve", "hazard", "time_to_event"], "forecasting": ["sequence", "distribution", "interval"],
        "graph": ["graph_indexed", "vector"], "process_prediction": ["scalar", "sequence", "time_to_event"],
        "spatiotemporal": ["spatial_field", "event_intensity"], "text_sequence": ["structured_labels", "vector"],
        "image_signal": ["scalar", "vector", "structured_labels"], "anomaly_change": ["scalar", "set"],
        "causal_uplift": ["scalar", "vector"], "probabilistic_bayesian": ["distribution"],
    }.get(group, ["scalar"])
    signal = {
        "weak_semisupervised": ["weakly_supervised", "semi_supervised", "positive_unlabeled", "active_learning"],
        "representation_selfsupervised": ["self_supervised_representation", "transfer"],
        "online_drift": ["online_supervised"],
    }.get(group, ["fully_supervised"])
    posture = {
        "survival_event_history": ["censored", "truncated", "competing_risk", "time_ordered"],
        "longitudinal_panel": ["grouped", "longitudinal", "panel", "missing"],
        "forecasting": ["time_ordered", "drifting"], "online_drift": ["time_ordered", "drifting"],
        "graph": ["network_dependent"], "process_prediction": ["event_process", "network_dependent", "time_ordered"],
        "spatiotemporal": ["spatial", "spatiotemporal"], "recommendation": ["selected", "exposure_biased", "grouped"],
        "missing_censoring": ["missing", "censored", "truncated", "selected"],
        "causal_uplift": ["intervention_affected", "selected"],
    }.get(group, ["iid_claimed", "grouped"])
    lower = name.lower()
    if "bayesian" in lower or group == "probabilistic_bayesian":
        epistemic = ["bayesian", "statistical"]
    elif any(token in lower for token in ("tree", "forest", "boost", "neighbor", "kernel", "graph", "neural", "network", "attention", "transformer", "lstm", "recurrent", "ensemble", "isotonic", "conformal")):
        epistemic = ["nonparametric", "statistical"]
    elif any(token in lower for token in ("cox", "gee", "generalized estimating", "causal", "uplift", "r-learner", "dr-learner")):
        epistemic = ["semiparametric", "frequentist", "statistical"]
    else:
        epistemic = ["parametric", "frequentist", "statistical"]
    timing = ["streaming_online", "event_triggered"] if group == "online_drift" else (["rolling_origin", "scheduled_refresh"] if group == "forecasting" else ["batch_prospective"])
    target_kind = {
        "classification": ["binary", "multiclass", "multilabel", "ordinal"], "count_compositional": ["count", "rate", "proportion"],
        "ranking": ["ranking"], "recommendation": ["recommendation"], "survival_event_history": ["time_to_event"],
        "forecasting": ["future_series"], "anomaly_change": ["anomaly", "change"], "graph": ["node", "edge", "graph"],
        "process_prediction": ["next_event", "remaining_time"], "causal_uplift": ["treatment_effect"],
        "spatiotemporal": ["spatial_response"], "text_sequence": ["structured_sequence"],
    }.get(group, ["continuous"])
    uncertainty = ["posterior", "distribution"] if "bayesian" in epistemic else (["prediction_set", "conformal_risk_bound"] if "conformal" in lower else ["none_justified", "prediction_interval", "distribution"])
    update = ["incremental", "sliding_window", "state_resettable"] if group == "online_drift" else ["immutable_fit", "scheduled_refit", "triggered_refit"]
    evaluation = ["out_of_time", "rolling_origin"] if group in {"forecasting", "online_drift", "process_prediction"} else (["survival_censoring_aware", "out_of_time"] if group == "survival_event_history" else (["spatial_block", "out_of_time"] if group == "spatiotemporal" else ["group_holdout", "nested_cv"]))
    return {"output_geometry": geometry, "learning_signal": signal, "data_generating_posture": posture, "epistemic_family": epistemic, "prediction_timing": timing, "decision_proximity": ["decision_support", "human_review_required"], "target_kind": target_kind, "uncertainty_form": uncertainty, "update_posture": update, "evaluation_posture": evaluation}


MODEL_GROUPS = {
    "regression": ["ordinary least squares", "weighted least squares", "generalized least squares", "ridge regression", "lasso regression", "elastic net regression", "least absolute deviations regression", "Huber robust regression", "Theil-Sen regression", "RANSAC regression", "quantile regression", "isotonic regression", "spline regression", "principal component regression", "partial least squares regression"],
    "classification": ["binary logistic regression", "multinomial logistic regression", "probit classification", "complementary log-log classification", "cumulative-link ordinal regression", "multilabel one-vs-rest", "error-correcting output codes", "linear discriminant analysis", "quadratic discriminant analysis", "Gaussian naive Bayes", "multinomial naive Bayes", "complement naive Bayes", "Bernoulli naive Bayes", "nearest-neighbor classification", "nearest-centroid classification", "perceptron", "passive-aggressive classification", "cost-sensitive logistic classification"],
    "count_compositional": ["Poisson regression", "quasi-Poisson regression", "negative-binomial regression", "zero-inflated Poisson", "zero-inflated negative binomial", "Poisson hurdle model", "negative-binomial hurdle model", "Tweedie regression", "Gamma regression", "inverse-Gaussian regression", "beta regression", "fractional logit", "Dirichlet regression", "multinomial compositional regression", "exposure-offset rate regression"],
    "tree_ensemble": ["CART regression tree", "CART classification tree", "conditional inference tree", "model tree", "bagged trees", "random forest classification", "random forest regression", "extremely randomized trees", "AdaBoost classification", "AdaBoost regression", "gradient boosted regression trees", "gradient boosted classification trees", "histogram gradient boosting", "XGBoost", "LightGBM", "CatBoost", "quantile gradient boosting", "monotonic gradient boosting", "NGBoost", "Bayesian additive regression trees", "explainable boosting machine", "random survival forest", "uplift tree", "causal forest"],
    "kernel_margin": ["linear support vector classification", "kernel support vector classification", "support vector regression", "nu support vector classification", "nu support vector regression", "one-class support vector machine", "kernel ridge regression", "kernel logistic regression", "Gaussian process regression", "Gaussian process classification", "sparse variational Gaussian process", "inducing-point Gaussian process", "Nystrom kernel approximation", "random Fourier feature model", "multiple-kernel learning"],
    "probabilistic_bayesian": ["Bayesian linear regression", "Bayesian logistic regression", "Bayesian generalized linear model", "hierarchical Bayesian regression", "Bayesian multilevel classification", "Bayesian additive regression trees", "Bayesian Gaussian process", "Bayesian dynamic linear model", "Bayesian structural time series", "Bayesian neural network", "latent-class regression", "mixture-of-experts prediction", "variational Bayesian prediction", "Laplace-approximated prediction", "Markov-chain Monte Carlo predictive model"],
    "calibration_ensemble": ["Platt scaling", "isotonic probability calibration", "temperature scaling", "vector scaling", "matrix scaling", "beta calibration", "histogram binning calibration", "Bayesian binning into quantiles", "bagging", "hard voting ensemble", "soft voting ensemble", "stacked generalization", "blending", "super learner", "dynamic ensemble selection", "deep ensemble", "split conformal regression", "cross-conformal prediction", "jackknife-plus prediction", "Mondrian conformal prediction", "adaptive prediction sets", "risk-controlling prediction", "conformalized quantile regression"],
    "ranking": ["pointwise regression ranking", "pointwise classification ranking", "RankSVM", "RankNet", "LambdaRank", "LambdaMART", "ListNet", "ListMLE", "coordinate ascent ranking", "pairwise logistic ranking", "Bayesian personalized ranking", "ordinal ranking model", "survival-based ranking", "counterfactual learning to rank", "fairness-constrained ranking"],
    "recommendation": ["user-based collaborative filtering", "item-based collaborative filtering", "explicit matrix factorization", "implicit weighted ALS", "probabilistic matrix factorization", "nonnegative matrix factorization recommender", "SVD++", "Bayesian personalized ranking recommender", "factorization machine recommender", "field-aware factorization machine", "SLIM sparse recommender", "content-based linear recommender", "hybrid recommender", "session-based Markov recommender", "sequence-aware recurrent recommender", "graph collaborative filtering", "contextual-bandit recommender", "calibrated recommender", "diversity-constrained reranker"],
    "survival_event_history": ["Kaplan-Meier conditional baseline", "Nelson-Aalen cumulative hazard", "Cox proportional hazards", "stratified Cox model", "time-varying Cox model", "penalized Cox model", "Aalen additive hazards", "Weibull accelerated failure time", "lognormal accelerated failure time", "log-logistic accelerated failure time", "generalized Gamma survival model", "Fine-Gray subdistribution hazards", "cause-specific hazards", "random survival forest", "survival support vector machine", "multi-task logistic regression survival", "DeepSurv", "DeepHit", "discrete-time hazard network", "joint longitudinal-survival model", "recurrent-event Andersen-Gill model", "multi-state survival model", "landmark dynamic prediction", "cure-fraction model"],
    "longitudinal_panel": ["entity fixed-effects regression", "random-intercept model", "random-slope mixed model", "generalized linear mixed model", "generalized estimating equations", "growth-curve model", "latent growth mixture model", "latent transition model", "dynamic panel regression", "difference-in-differences prediction component", "marginal structural model", "functional data regression", "longitudinal Gaussian process", "joint longitudinal-outcome model", "state-transition panel model"],
    "forecasting": ["naive forecast", "seasonal naive forecast", "moving-average forecast", "simple exponential smoothing", "Holt trend forecast", "damped-trend forecast", "Holt-Winters seasonal forecast", "ETS state-space forecast", "autoregressive model", "moving-average error model", "ARIMA", "SARIMA", "ARIMAX dynamic regression", "VAR", "VECM", "dynamic factor model", "unobserved-components model", "Kalman-filter state-space forecast", "structural time-series model", "Theta method", "TBATS", "Croston intermittent-demand forecast", "Syntetos-Boylan approximation", "Teunter-Syntetos-Babai forecast", "GARCH volatility forecast", "stochastic-volatility forecast", "Prophet decomposable forecast", "DeepAR", "N-BEATS", "N-HiTS", "temporal convolutional forecast", "recurrent neural forecast", "Temporal Fusion Transformer", "PatchTST", "TimesNet", "hierarchical forecast reconciliation", "temporal forecast reconciliation", "ensemble forecast", "quantile forecast", "distributional forecast"],
    "anomaly_change": ["standardized residual anomaly score", "robust MAD anomaly score", "Mahalanobis distance anomaly score", "Shewhart control chart", "EWMA control chart", "CUSUM change detector", "scan statistic", "Hotelling T-squared chart", "isolation forest", "local outlier factor", "one-class support vector machine", "elliptic envelope", "histogram-based outlier score", "PCA reconstruction anomaly", "robust PCA anomaly", "autoencoder reconstruction anomaly", "variational autoencoder anomaly score", "matrix profile discord", "spectral residual anomaly", "k-nearest-neighbor outlier score", "density-ratio change detection", "binary segmentation changepoint", "PELT changepoint", "windowed changepoint", "Bayesian online changepoint detection", "hidden-Markov regime change"],
    "online_drift": ["online stochastic-gradient regression", "online logistic regression", "passive-aggressive online learner", "Hoeffding tree", "Hoeffding adaptive tree", "online bagging", "adaptive random forest", "dynamic weighted majority", "streaming k-nearest neighbors", "online naive Bayes", "ADWIN drift detector", "DDM drift detector", "EDDM drift detector", "Page-Hinkley drift detector", "KSWIN drift detector", "HDDM drift detector", "drift-triggered retraining", "sliding-window learner", "fading-factor learner", "recurring-concept ensemble"],
    "graph": ["common-neighbors link prediction", "Jaccard link prediction", "Adamic-Adar link prediction", "preferential-attachment link prediction", "Katz link prediction", "matrix-factorization link prediction", "DeepWalk embedding predictor", "node2vec embedding predictor", "graph-convolutional network", "GraphSAGE", "graph attention network", "relational graph convolutional network", "heterogeneous graph transformer", "graph isomorphism network", "temporal graph network", "temporal graph attention network", "dynamic graph recurrent network", "graph-level classifier", "node classifier", "edge classifier", "knowledge-graph translational scorer", "temporal knowledge-graph scorer", "graph anomaly detector", "subgraph matching predictor", "graph survival predictor"],
    "process_prediction": ["trace-prefix next-activity classifier", "trace-prefix next-event-time regressor", "trace-prefix remaining-time regressor", "trace-prefix outcome classifier", "trace-prefix SLA-breach classifier", "trace-prefix compliance-risk predictor", "Markov process predictor", "hidden-Markov process predictor", "prefix-aggregation gradient boosting", "LSTM process predictor", "temporal-convolution process predictor", "attention process predictor", "process-transformer predictor", "object-centric handcrafted-feature predictor", "object-interaction feature predictor", "heterogeneous object-event graph predictor", "object-centric graph-embedding predictor", "temporal event-knowledge-graph predictor", "state-aware OCEL predictor", "multi-object next-activity predictor", "multi-object remaining-time predictor", "process concept-drift predictor"],
    "spatiotemporal": ["ordinary kriging", "universal kriging", "co-kriging", "Gaussian-process spatial regression", "spatial autoregressive lag model", "spatial error model", "conditional autoregressive model", "simultaneous autoregressive model", "geographically weighted regression", "geographically and temporally weighted regression", "spatial Durbin model", "spatiotemporal state-space model", "spatiotemporal Gaussian process", "Hawkes point-process predictor", "log-Gaussian Cox point process", "spatial scan statistic", "trajectory destination predictor", "trajectory travel-time predictor", "raster convolutional predictor", "spatiotemporal graph neural predictor"],
    "weak_semisupervised": ["self-training classifier", "co-training classifier", "tri-training classifier", "label propagation", "label spreading", "semi-supervised support vector machine", "positive-unlabeled Elkan-Noto learner", "nonnegative positive-unlabeled risk learner", "weak-supervision label model", "data-programming discriminative learner", "multi-instance learning", "learning from label proportions", "consistency-regularized classifier", "pseudo-labeling", "graph-based semi-supervised learner", "active-learning uncertainty sampler", "active-learning query-by-committee", "crowd-label Dawid-Skene model"],
    "missing_censoring": ["complete-case predictive model", "missing-indicator predictive model", "single mean-mode imputation", "k-nearest-neighbor imputation", "multiple imputation by chained equations", "joint-model multiple imputation", "MissForest imputation", "matrix-completion imputation", "inverse-probability weighted prediction", "doubly robust missing-outcome prediction", "pattern-mixture sensitivity model", "selection-model sensitivity analysis", "tobit censored regression", "interval-censored regression", "left-truncation-aware survival prediction", "coarsening-at-random model", "joint missingness-outcome model", "informative-censoring weighted model"],
    "causal_uplift": ["T-learner", "S-learner", "X-learner", "R-learner", "DR-learner", "causal forest", "generalized random forest", "orthogonal random forest", "Bayesian causal forest", "uplift decision tree", "uplift random forest", "class-transformation uplift model", "two-model incremental response", "transformed-outcome regression", "targeted maximum-likelihood CATE", "causal boosting", "policy-learning score model", "treatment-effect neural network", "dose-response learner", "survival treatment-effect learner"],
    "interpretable_symbolic": ["sparse linear scorecard", "monotonic scorecard", "decision list", "Bayesian rule list", "RuleFit", "falling rule list", "generalized additive model", "explainable boosting machine", "shape-constrained additive model", "monotonic lattice model", "fuzzy rule-based classifier", "Takagi-Sugeno fuzzy predictor", "symbolic regression", "genetic-programming symbolic model", "optimal classification tree", "supersparse linear integer model", "prototype classifier", "case-based reasoning predictor"],
    "text_sequence": ["TF-IDF logistic text classifier", "TF-IDF linear SVM text classifier", "multinomial naive-Bayes text classifier", "NB-SVM text classifier", "character n-gram classifier", "conditional random field sequence tagger", "hidden-Markov sequence classifier", "maximum-entropy Markov model", "convolutional text classifier", "recurrent sequence classifier", "bidirectional recurrent sequence tagger", "attention sequence classifier", "non-generative transformer encoder classifier", "Siamese sentence-pair classifier", "learning-to-rank document scorer", "topic-proportion downstream classifier"],
    "image_signal": ["HOG plus SVM image classifier", "bag-of-visual-words classifier", "linear spectral classifier", "wavelet-feature classifier", "matched-filter detector", "Kalman signal predictor", "autoregressive spectral predictor", "convolutional neural image classifier", "residual network classifier", "vision transformer classifier", "temporal convolution signal classifier", "recurrent signal classifier", "spectrogram convolution classifier", "self-supervised encoder plus linear probe", "object detector", "semantic segmentation predictor", "time-frequency anomaly detector", "fault-diagnosis vibration classifier"],
    "representation_selfsupervised": ["SimCLR representation learner", "MoCo representation learner", "BYOL representation learner", "DINO representation learner", "Barlow Twins representation learner", "VICReg representation learner", "masked-feature tabular encoder", "contrastive time-series encoder", "temporal-neighborhood coding", "graph contrastive encoder", "self-supervised graph pretrainer", "multiview canonical representation learner", "autoencoder representation learner", "denoising autoencoder representation learner", "metric-learning Siamese encoder"],
}


SOURCE_BY_GROUP = {
    "regression": ["glm_nelder", "lasso", "elastic_net", "quantile_regression", "gam", "statsmodels_user"],
    "classification": ["hinge_svm", "knn_cover", "sklearn_user"],
    "count_compositional": ["glm_nelder", "statsmodels_user"],
    "tree_ensemble": ["cart", "random_forest", "adaboost", "gradient_boost", "xgboost_paper", "lightgbm_paper", "catboost_paper", "ngboost", "bart"],
    "kernel_margin": ["hinge_svm", "gp_rasmussen", "kernel_pca", "sklearn_user"],
    "probabilistic_bayesian": ["stan_reference", "pymc_api", "gp_rasmussen", "bart"],
    "calibration_ensemble": ["platt_scaling", "isotonic_cal", "temperature_scaling", "beta_calibration", "stacking", "super_learner", "split_conformal", "jackknife_plus", "conformal_classification"],
    "ranking": ["ranksvm", "ranknet", "lambdarank", "listnet", "bpr"],
    "recommendation": ["matrix_factorization", "implicit_als", "factorization_machine", "bpr", "slim"],
    "survival_event_history": ["cox_ph", "kaplan_meier", "fine_gray", "random_survival_forest", "deepsurv", "deephit", "mtlr", "joint_models"],
    "longitudinal_panel": ["gee", "mixed_models", "joint_models"],
    "forecasting": ["forecasting_fpp3", "ets_state_space", "theta", "croston", "prophet", "deep_ar", "nbeats", "nhits", "tft", "patchtst", "timesnet", "garch", "forecast_reconciliation"],
    "anomaly_change": ["isolation_forest", "lof", "one_class_svm", "matrix_profile", "pelt", "bocpd"],
    "online_drift": ["river_docs", "adwin", "hoeffding_tree", "adaptive_rf"],
    "graph": ["deepwalk", "node2vec", "gcn", "graphsage", "gat", "rgcn", "tgn", "tgat", "hetero_graph_transformer"],
    "process_prediction": ["process_predictive_survey", "ocppa", "hoeg", "tekg", "sa_ocpm", "oced_core", "ekg_fahland", "docel", "cases_ocel", "concept_drift_actor", "ocel20"],
    "spatiotemporal": ["kriging", "gwr", "hawkes", "ogc_sfa", "proj_docs"],
    "weak_semisupervised": ["label_model", "positive_unlabeled", "label_propagation", "cotrain"],
    "missing_censoring": ["mice", "missforest", "joint_models", "cox_ph"],
    "causal_uplift": ["causal_forest", "xlearner", "rlearner", "drlearner", "uplift_tree", "dowhy_docs", "econml_docs"],
    "interpretable_symbolic": ["rulefit", "ebm", "lime", "shap", "anchor"],
    "text_sequence": ["crf", "hmm", "tfidf", "unicode15"],
    "image_signal": ["hog", "resnet", "vit", "scipy_signal", "opencv_docs"],
    "representation_selfsupervised": ["simclr", "byol", "dino"],
}


DECISION_NAMES = [
    "prediction target identity", "target population", "unit of prediction", "decision recipient", "actionability contract", "prediction horizon", "forecast origin", "label definition", "label observation delay", "label finality", "label censoring", "label adjudication", "positive class", "class ontology", "ordinal ordering", "multilabel dependence", "cost matrix", "abstention policy", "selective coverage", "feature definition", "feature availability time", "feature freshness", "feature point-in-time join", "feature transformation", "feature scaling", "feature categorical encoding", "unknown category", "rare category", "feature missingness", "feature provenance", "proxy feature prohibition", "post-outcome leakage guard", "group leakage guard", "duplicate entity guard", "temporal cutoff", "train validation split", "calibration split", "test split", "external validation", "cross-validation scheme", "nested cross-validation", "rolling-origin evaluation", "blocked spatial validation", "clustered validation", "bootstrap scheme", "sampling weights", "survey design", "class imbalance strategy", "negative sampling", "candidate generation", "exposure correction", "position-bias correction", "censoring model", "competing-risk definition", "time origin", "time scale", "left truncation", "recurrent event handling", "missingness mechanism", "imputation model", "imputation count", "sensitivity analysis", "identification reference", "treatment definition", "treatment timing", "propensity overlap", "nuisance cross-fitting", "estimand kind", "loss function", "proper scoring rule", "regularization", "monotonicity constraint", "interaction constraint", "fairness constraint", "sparsity constraint", "parameter prior", "hyperparameter search space", "hyperparameter optimizer", "early stopping", "random seed", "random stream splitting", "numeric precision", "determinism level", "parallel reduction law", "device target", "memory budget", "training work budget", "inference latency budget", "batch size", "online update cadence", "online state retention", "drift detector", "drift threshold", "drift response", "retraining trigger", "champion challenger", "calibration method", "calibration metric", "decision threshold", "threshold ownership", "conformal score", "conformal miscoverage", "coverage group policy", "prediction interval kind", "uncertainty decomposition", "evaluation metric", "metric aggregation", "subgroup evaluation", "fairness metric", "robustness evaluation", "distribution-shift suite", "adversarial test", "explanation method", "explanation audience", "explanation fidelity", "explanation stability", "model serialization", "model signature", "artifact digest", "provider version", "provider qualification", "fallback model", "failure disposition", "partial result policy", "monitoring window", "performance lag", "alert threshold", "human review", "rollback trigger", "retirement policy", "record retention", "privacy purpose", "protected attribute access", "audit evidence", "vertical approval authority",
]


LIBRARY_SPECS = [
    ("target_contracts", "semantic", "prediction target, population, horizon and action contract"),
    ("label_contracts", "semantic", "label observation, finality, censoring and adjudication"),
    ("feature_contracts", "semantic", "point-in-time feature definition and availability"),
    ("split_planner", "planning", "entity, group, temporal, spatial and nested data partitions"),
    ("leakage_guard", "validation", "post-outcome, group, duplicate and temporal leakage detection"),
    ("sampling_weights", "method", "survey, inverse-probability and class weights"),
    ("regression_models", "method", "typed regression family definitions"),
    ("classification_models", "method", "typed classification family definitions"),
    ("count_models", "method", "count, exposure, hurdle and zero-inflation definitions"),
    ("tree_models", "method", "tree and ensemble semantic configurations"),
    ("kernel_models", "method", "kernel and margin contracts"),
    ("probabilistic_models", "method", "probabilistic graph and posterior predictive contracts"),
    ("survival_models", "method", "censoring and competing-risk model contracts"),
    ("longitudinal_models", "method", "panel and repeated-measure model contracts"),
    ("forecast_models", "method", "origin/horizon-qualified forecasting contracts"),
    ("ranking_models", "method", "query, candidate and listwise ranking contracts"),
    ("recommender_models", "method", "exposure-aware recommendation contracts"),
    ("graph_models", "method", "typed static/temporal graph prediction contracts"),
    ("process_prediction_models", "method", "trace/object/event-graph process prediction contracts"),
    ("spatial_models", "method", "CRS/support-qualified spatial prediction contracts"),
    ("online_models", "method", "ordered incremental-update and state contracts"),
    ("weak_supervision", "method", "label-source and semi-supervised contracts"),
    ("causal_effect_learners", "method", "effect learner contracts requiring external identification"),
    ("interpretable_models", "method", "rule, additive, monotonic and symbolic model contracts"),
    ("neural_predictive_models", "method", "non-generative neural predictive architecture contracts"),
    ("objective_functions", "algorithm", "typed losses, likelihoods and proper scoring rules"),
    ("optimizers", "algorithm", "bounded iterative optimization with convergence receipt"),
    ("linear_solvers", "kernel", "qualified dense/sparse linear system solving"),
    ("factorization_kernels", "kernel", "matrix and tensor factorization primitives"),
    ("tree_training_kernels", "kernel", "histogram, split scoring and partition kernels"),
    ("tree_inference_kernels", "kernel", "branch and compiled ensemble inference"),
    ("kernel_matrix_ops", "kernel", "kernel construction and approximation primitives"),
    ("neighbor_search", "kernel", "exact/approximate neighbor search with distance contract"),
    ("graph_sampling", "kernel", "typed neighborhood and temporal graph sampling"),
    ("graph_message_passing", "kernel", "typed graph aggregation and attention kernels"),
    ("sequence_kernels", "kernel", "dynamic programming and sequence recurrence kernels"),
    ("tensor_autodiff", "kernel", "tensor execution and automatic differentiation"),
    ("signal_features", "kernel", "sampling-qualified signal transforms"),
    ("image_features", "kernel", "coordinate-qualified image feature primitives"),
    ("calibration", "evaluation", "held-out probability and score calibration"),
    ("conformal_prediction", "evaluation", "exchangeability-qualified prediction sets/intervals"),
    ("metrics", "evaluation", "typed point, probabilistic, ranking and survival metrics"),
    ("fairness_evaluation", "evaluation", "authorized subgroup fairness measurements"),
    ("robustness_evaluation", "evaluation", "shift, perturbation and stress tests"),
    ("explanation", "evaluation", "bounded fidelity/stability explanation artifacts"),
    ("model_selection", "planning", "nested tuning and multiple-comparison-aware selection"),
    ("artifact_manifest", "artifact", "model/config/data/code/provider digests"),
    ("model_serialization", "artifact", "versioned portable fitted-artifact envelope"),
    ("model_registry_port", "integration", "pure registry port without product coupling"),
    ("batch_scoring", "runtime", "bounded batch prediction"),
    ("online_scoring", "runtime", "bounded low-latency prediction"),
    ("stream_scoring", "runtime", "ordered stateful stream prediction"),
    ("monitoring", "runtime", "data/performance/calibration/drift observations"),
    ("drift_response", "policy", "authorized alert, shadow, retrain, rollback transitions"),
    ("model_lifecycle", "policy", "candidate, qualified, deployed, degraded and retired states"),
    ("provider_adapter_sklearn", "adapter", "scikit-learn DTO/fit/predict boundary"),
    ("provider_adapter_statsmodels", "adapter", "statsmodels formula/result boundary"),
    ("provider_adapter_xgboost", "adapter", "XGBoost matrix/model boundary"),
    ("provider_adapter_onnx", "adapter", "ONNX graph/runtime boundary"),
    ("provider_adapter_torch", "adapter", "PyTorch module/tensor boundary"),
]


INNOVATION_SPECS = [
    ("adaptive_prediction_sets", 2021, "conformal_classification", "adaptive set-valued classification", "coverage depends on exchangeability and the exact calibration protocol"),
    ("label_shift_uq", 2021, "label_shift_cp", "reweighted conformal/calibration under label shift", "requires a valid label-shift model and target-distribution information"),
    ("jackknife_plus", 2021, "jackknife_plus", "cross-fitted predictive intervals", "computational cost and assumptions vary by variant"),
    ("risk_controlling_prediction", 2022, "risk_controlling", "finite-sample control of declared predictive risk", "only the declared loss/risk and sampling assumptions are controlled"),
    ("modular_conformal_calibration", 2022, "modular_conformal", "model-agnostic distribution recalibration", "needs held-out calibration observations and does not repair target misspecification"),
    ("nhits", 2022, "nhits", "hierarchical interpolation neural forecasting", "benchmark evidence does not imply dominance at every horizon or data regime"),
    ("patchtst", 2023, "patchtst", "patch-based channel-independent forecasting", "channel-independence can discard cross-series structure"),
    ("timesnet", 2023, "timesnet", "period-aware two-dimensional time-series modeling", "period extraction and benchmark settings bound applicability"),
    ("tabpfn", 2022, "tabpfn", "prior-data-fitted small-tabular classification", "task-size, feature and prior assumptions are material"),
    ("ft_transformer", 2021, "ft_transformer", "strong transformer baseline for tabular prediction", "trees remain competitive; no universal neural superiority"),
    ("tabtransformer", 2021, "tabtransformer", "contextual categorical embeddings", "requires category stability and careful unknown-category semantics"),
    ("tft_adoption", 2021, "tft", "multi-horizon gating and attention forecast architecture", "attention is not a causal explanation"),
    ("dino", 2021, "dino", "self-distilled vision representation learning", "learned invariances depend on augmentation and pretraining corpus"),
    ("object_centric_predictive", 2022, "ocppa", "interaction-aware object-centric process prediction", "evaluation domains and chosen KPI targets constrain evidence"),
    ("hoeg", 2024, "hoeg", "heterogeneous object-event graph encoding for predictive monitoring", "benefit depends on informative object attributes/interactions and evaluated logs"),
    ("temporal_ekg", 2024, "tekg", "snapshot-preserving temporal event knowledge graphs", "representation transform is not itself a validated predictor"),
    ("sa_ocpm", 2025, "sa_ocpm", "explicit object-state transition events and state-aware event projection", "state derivation rules and epsilon ordering are domain decisions, not universal facts"),
    ("oced_core", 2024, "oced_core", "minimal object-centric event-data core and explicit extension design space", "known relation/time/type ambiguities remain outside the minimal core"),
    ("actor_process_drift", 2024, "concept_drift_actor", "actor-aware multi-perspective process drift detection", "detected drift does not identify cause or prescribe adaptation"),
    ("vision_transformer", 2021, "vit", "patch-token predictive vision architecture", "requires qualification for image scale, data regime and compute"),
    ("causal_drlearner", 2021, "drlearner", "doubly robust heterogeneous-effect learning", "identification, overlap and nuisance-rate conditions remain external proof obligations"),
    ("distribution_shift_evaluation", 2023, "dream", "increased emphasis on distributionally robust evaluation", "proceedings index is discovery evidence, not a single method contract"),
    ("conformal_time_series", 2023, "forecasting_conformal", "dependence-aware conformal inference for time series", "coverage laws depend on the chosen dependence and randomization conditions"),
    ("selective_prediction", 2021, "selective_classification", "risk-coverage rejection for predictive deployment", "abstention transfers work and risk to a fallback actor"),
    ("graph_temporal_memory", 2021, "tgn", "memory-based prediction on dynamic graphs", "event ordering, negative sampling and memory staleness must be bound"),
    ("heterogeneous_graph_attention", 2021, "hetero_graph_transformer", "typed graph attention for heterogeneous predictions", "schema and type coverage may not transfer"),
    ("risk_aware_fair_reductions", 2021, "fair_reductions", "production adoption of constraint-based fairness reduction", "group metric parity is not individual fairness or legal compliance"),
    ("onnx_operator_expansion", 2024, "onnx_spec", "broader portable predictive operator contracts", "operator presence is not bitwise cross-runtime equivalence"),
    ("compiled_tree_inference", 2023, "treelite_docs", "portable compiled tree-ensemble inference", "requires exact front-end conversion and target qualification"),
    ("process_context_graphs", 2026, "ekg_fahland", "event-knowledge-graph context for multidimensional process behavior", "2026 extensions require separate evidence; base source is 2022"),
    ("object_centric_case_research", 2022, "cases_ocel", "explicit case/variant projections over object-centric event data", "projection choice can lose interactions and must not be treated as canonical"),
    ("data_aware_ocel", 2023, "docel", "unambiguous linkage of dynamic attributes to objects/events", "DOCEL and OCEL 2.0 are related but not interchangeable specifications"),
    ("probabilistic_boosting", 2021, "ngboost", "growing use of proper-score probabilistic boosting", "distribution family and score selection bound claims"),
    ("global_neural_forecasting", 2022, "deep_ar", "mature global probabilistic forecasting practice", "cross-series pooling can cause negative transfer"),
    ("selfsupervised_transfer", 2021, "simclr", "non-generative self-supervised transfer into predictive tasks", "pretraining overlap and representation leakage require audit"),
    ("tabnet_attention", 2021, "tabnet", "sequential feature attention for tabular prediction", "attention masks are not causal or complete explanations"),
    ("saint_tabular_pretraining", 2021, "saint", "row/column attention and contrastive tabular pretraining", "pretraining overlap and category drift require qualification"),
    ("autoformer", 2021, "autoformer", "decomposition/autocorrelation long-horizon forecasting", "reported benchmark settings do not establish universal horizon accuracy"),
    ("fedformer", 2022, "fedformer", "frequency-enhanced decomposed forecasting", "frequency truncation and decomposition choices can discard signal"),
    ("dlinear_benchmark_correction", 2023, "dlinear", "simple decomposition-linear baselines that challenged complex forecasters", "benchmark protocol and dataset properties bound the conclusion"),
    ("tide", 2023, "tide", "dense encoder-decoder multi-horizon forecasting", "covariate availability and retraining regime remain explicit decisions"),
    ("tsmixer", 2023, "tsmixer", "all-MLP time/feature mixing forecasts", "cross-variate mixing and context length require data-specific validation"),
    ("itransformer", 2024, "itransformer", "variate-token inverted attention forecasts", "architecture novelty is not evidence of production superiority"),
    ("timemixer", 2024, "timemixer", "multiscale decomposable mixing forecasts", "scale choices and benchmark horizons constrain claims"),
    ("tabr", 2024, "tabr", "learned retrieval from training examples for discriminative tabular prediction", "retrieval corpus identity, leakage and latency are part of the fitted artifact"),
    ("modernnca", 2024, "modernnca", "modern learned-neighborhood tabular predictor", "neighbor index, metric and training corpus must be versioned"),
    ("realmlp", 2024, "realmlp", "strong pre-tuned tabular neural and tree baselines", "pre-tuned defaults remain dataset- and budget-dependent"),
    ("graphgps", 2022, "graphgps", "hybrid local/global graph predictive architecture", "positional encoding, graph size and attention cost require target qualification"),
    ("graphmae", 2022, "graphmae", "masked-feature self-supervised graph representations", "mask task quality does not guarantee downstream target utility"),
    ("dygformer", 2023, "dygformer", "interaction-sequence modeling for dynamic graph prediction", "history sampling and negative sampling materially affect evaluation"),
    ("temporal_graph_benchmark", 2023, "tgb", "stricter datasets and evaluation protocols for dynamic link prediction", "a benchmark score remains task-scoped, not universal superiority"),
    ("anomaly_transformer", 2022, "anomaly_transformer", "association-discrepancy anomaly scoring", "thresholding and contamination assumptions remain deployment decisions"),
    ("tranad", 2022, "tranad", "multivariate temporal anomaly scoring architecture", "reconstruction success is not root-cause diagnosis"),
    ("dcdetector", 2023, "dcdetector", "contrastive time-series anomaly representation", "reported labels and benchmark contamination constrain evidence"),
    ("survtrace", 2022, "survtrace", "competing-event neural survival prediction", "censoring, calibration and external validation remain mandatory"),
    ("conformal_risk_control", 2024, "conformal_risk_control", "distribution-free control for declared monotone predictive risks", "guarantees are only as broad as the risk family and exchangeability conditions"),
]


def method_specific_law(name: str, group: str) -> str:
    lower = name.lower()
    if "conformal" in lower or "prediction set" in lower:
        return "Coverage is scoped to the explicit exchangeability/shift condition, calibration split, score, randomization and finite sample; it is not per-instance certainty."
    if "object-centric" in lower or "ocel" in lower or "event-knowledge" in lower or "object-event graph" in lower or "multi-object" in lower:
        return "Object, event, relation, time-varying attribute and observation-cutoff semantics must survive representation; a flattened case trace is a lossy projection."
    if "survival" in lower or "hazard" in lower or "cox" in lower:
        return "Time origin, censoring, truncation, event type and target functional must be explicit; ranking concordance is not probability calibration."
    if "uplift" in lower or "causal" in lower or "treatment" in lower:
        return "Predictive fit does not establish causal identification; an external identification/refutation artifact is mandatory."
    if "forecast" in lower or group == "forecasting":
        return "Every feature is classified by availability at the forecast origin; random row splitting is prohibited."
    if "calibr" in lower:
        return "Calibration must be evaluated on observations not used to fit either the base predictor or the calibrator and at the decision-relevant grouping."
    return f"{name} may be selected only when its support, assumptions, objective, approximation and output contract match the resolved prediction target."


MODELS: list[dict] = []
OPERATIONS: list[dict] = []
MAPPINGS: list[dict] = []
MODEL_SOURCE_OVERRIDES = {
    "object-centric handcrafted-feature predictor": ["ocel20", "ocppa"],
    "object-interaction feature predictor": ["ocppa", "oced_core"],
    "heterogeneous object-event graph predictor": ["hoeg", "ocel20"],
    "object-centric graph-embedding predictor": ["hoeg", "ocppa"],
    "temporal event-knowledge-graph predictor": ["tekg", "ekg_fahland"],
    "state-aware OCEL predictor": ["sa_ocpm", "ocel20"],
    "multi-object next-activity predictor": ["hoeg", "ocppa"],
    "multi-object remaining-time predictor": ["hoeg", "ocppa"],
    "process concept-drift predictor": ["concept_drift_actor", "ekg_fahland"],
}
for group, names in MODEL_GROUPS.items():
    target, data, assumptions, objective, output = GROUP_CONTRACTS[group]
    source_keys = SOURCE_BY_GROUP[group]
    for index, name in enumerate(names):
        mid = f"predictive_model.{group}.{slug(name)}"
        selected_sources = MODEL_SOURCE_OVERRIDES.get(name, [source_keys[index % len(source_keys)], source_keys[(index + 1) % len(source_keys)]])
        source_refs = [f"source.predictive.{key}" for key in selected_sources]
        MODELS.append({
            "model_family_id": mid, "edition": EDITION, "status": "sourced_candidate",
            "name": name, "family": group, "llm_dependency": "none",
            "axis_bindings": axis_bindings(group, name),
            "prediction_target_contract": target,
            "input_contract": data,
            "feature_label_contract": "Features and labels carry definition, owner, entity grain, valid/recorded/available time, provenance and point-in-time join policy.",
            "study_split_contract": "Fit, tune, calibrate and final evaluation partitions are distinct according to entity/group/time/spatial dependence; leakage checks are blocking.",
            "assumptions": [assumptions, method_specific_law(name, group)],
            "objective_contract": objective,
            "algorithm_contract": "A finite fitting procedure declares initialization, update order, convergence/termination, randomness, approximation, numeric and work-budget laws.",
            "kernel_requirements": ["typed linear/algebraic, tree, neighbor, graph, tensor or sequence primitives selected from resolved algorithm", "qualified target precision/layout/device behavior"],
            "fitted_artifact_contract": "Carries model family, target, features, split, objective, algorithm, provider, target, hyperparameters, seeds and training-data/code/config digests.",
            "prediction_output_contract": output,
            "calibration_evaluation_contract": "Evaluation uses target-appropriate discrimination, calibration, utility, uncertainty and subgroup measures; metric selection precedes final evaluation.",
            "deployment_monitoring_contract": "Observe input validity, freshness, shift, performance when labels mature, calibration, resource use, failures and policy transitions.",
            "failure_states": ["invalid_input", "target_unresolved", "assumptions_unmet", "leakage_detected", "not_identified", "not_converged", "numerically_suspect", "unsupported_target", "budget_exhausted", "cancelled", "partial_prediction", "stale_artifact", "out_of_scope"],
            "explainability_limits": "Explanation artifacts are method- and audience-scoped; feature attribution, attention, coefficients and local surrogates are not causal proof.",
            "fairness_safety_contract": "Protected-group use and metrics require authority; aggregate parity does not establish individual fairness, safety or legal compliance.",
            "complexity_contract": "Training/inference time, memory, state growth and parallelism are provider- and shape-qualified, never inferred from family name alone.",
            "invalidation_triggers": ["target or label redefinition", "feature availability/provenance change", "split contamination", "provider/algorithm change", "material drift or calibration failure", "policy or authority change"],
            "source_refs": source_refs,
            "gaps": ["Applicability to each vertical, target and deployed provider remains open until qualified evidence exists."],
        })
        op_specs = [
            ("resolve_target", "semantic", "resolve prediction target, population, horizon, action and authority"),
            ("plan_study", "planning", "construct leakage-safe fit/tune/calibration/evaluation partitions"),
            ("fit", "training", "fit declared objective within finite budgets and emit diagnostics"),
            ("predict", "inference", "produce typed prediction or explicit partial/refusal state"),
            ("evaluate", "evaluation", "evaluate declared measures on untouched observations when labels mature"),
        ]
        for suffix, phase, semantics in op_specs:
            OPERATIONS.append({
                "operation_id": f"operation.{mid}.{suffix}", "edition": EDITION,
                "model_family_ref": mid, "name": suffix, "phase": phase, "semantics": semantics,
                "input_contract": "typed prediction-study or fitted-artifact state",
                "output_contract": "typed state transition plus evidence receipt",
                "preconditions": ["all phase-owned decisions resolved", "required authority and finite resource budget present"],
                "effects": [] if phase in {"semantic", "planning", "evaluation"} else ["compute", "artifact_write"],
                "partiality": ["refused", "unsupported", "cancelled", "budget_exhausted", "non_converged", "numerically_suspect"],
                "determinism": "Determinism class, randomness and provider target are explicit.",
            })
        MAPPINGS.append({
            "mapping_id": f"mapping.{mid}", "edition": EDITION, "subject_ref": mid,
            "canonical_nodes": {
                "practice": f"analytics.predictive.{group}", "study_definition": "study_definition.predictive",
                "estimand": f"estimand.predictive.{group}", "analytical_model": mid,
                "estimator": f"estimator.{mid}", "analytical_method": f"analytical_method.{mid}",
                "algorithm": f"algorithm.{mid}.selected", "kernel_contract": f"kernel_contract.{mid}.resolved",
                "fitted_artifact": f"fitted_artifact_type.{mid}", "evaluation_result": f"evaluation_result.{mid}",
            },
            "compiler_edges": ["targets", "estimates", "fits", "realized_by", "executes_as", "qualified_for", "evaluates"],
            "binding_law": "Resolve semantic and evidence nodes before algorithm, kernel, provider and target binding; unknown mapping is a typed compiler gap.",
        })


# These are distinct compiler nodes even when one paper or package implements several of them.
COMPONENT_GRAPH: list[dict] = []
COMPONENT_EDGES: list[dict] = []
EVIDENCE_EDGES: list[dict] = []
for model in MODELS:
    mid = model["model_family_id"]
    group = model["family"]
    components = [
        ("predictive_task", f"predictive_task.{mid}", model["prediction_target_contract"]),
        ("model_family", mid, model["assumptions"]),
        ("model_structure", f"model_structure.{mid}", f"Structure/configuration for {model['name']}; distinct from fitted parameter values."),
        ("objective_loss", f"objective_loss.{mid}", model["objective_contract"]),
        ("estimator", f"estimator.{mid}", "Maps the declared study observations to a fitted artifact under the objective and assumptions."),
        ("optimization_training_algorithm", f"algorithm.{mid}.selected", model["algorithm_contract"]),
        ("representation", f"representation_binding.{mid}", {"requirement_ref": f"representation_requirement.predictive.{group}", "input_contract": model["input_contract"]}),
        ("kernel", f"kernel_contract.{mid}.resolved", model["kernel_requirements"]),
        ("fitted_artifact", f"fitted_artifact_type.{mid}", model["fitted_artifact_contract"]),
        ("calibration", f"calibration_contract.{mid}", model["calibration_evaluation_contract"]),
        ("evaluator", f"evaluator.{mid}", model["calibration_evaluation_contract"]),
        ("decision_rule", f"decision_rule.{mid}", "Transforms a prediction into abstain/review/recommend/act under explicit threshold, cost, authority and fallback policy."),
    ]
    for kind, cid, contract in components:
        COMPONENT_GRAPH.append({
            "component_id": cid, "edition": EDITION, "component_kind": kind,
            "model_family_ref": mid, "contract": contract,
            "source_refs": model["source_refs"],
            "non_collapse_law": "Identity is owned by component kind; sharing one package, class or paper does not merge semantic nodes.",
        })
    edge_specs = [
        ("predictive_task", "targets", "model_family"), ("model_family", "has_structure", "model_structure"),
        ("model_family", "estimated_by", "estimator"), ("estimator", "optimizes", "objective_loss"),
        ("estimator", "trained_by", "optimization_training_algorithm"), ("optimization_training_algorithm", "executes_over", "kernel"),
        ("representation", "is_input_to", "estimator"), ("estimator", "produces", "fitted_artifact"),
        ("fitted_artifact", "calibrated_by", "calibration"), ("fitted_artifact", "evaluated_by", "evaluator"),
        ("fitted_artifact", "feeds", "decision_rule"),
    ]
    comp_by_kind = {kind: cid for kind, cid, _ in components}
    for ordinal, (src_kind, relation, dst_kind) in enumerate(edge_specs):
        COMPONENT_EDGES.append({
            "edge_id": f"component_edge.{slug(mid)}.{ordinal:02d}", "edition": EDITION,
            "from_ref": comp_by_kind[src_kind], "relation": relation, "to_ref": comp_by_kind[dst_kind],
        })
    for source_ref in model["source_refs"]:
        EVIDENCE_EDGES.append({
            "evidence_edge_id": f"evidence_edge.{slug(source_ref)}.{slug(mid)}", "edition": EDITION,
            "source_ref": source_ref, "relation": "supports_candidate_contract", "subject_ref": mid,
            "claim_scope": "named family definitions/implementation evidence only; not universal superiority or deployment conformance",
        })


DECISIONS = []
for name in DECISION_NAMES:
    DECISIONS.append({
        "decision_id": f"decision.predictive.{slug(name)}", "edition": EDITION,
        "question": f"What is the authorized {name}?", "owner_context_ref": "context.predictive_model_governance",
        "value_contract": f"{''.join(word.title() for word in slug(name).split('_'))}Spec",
        "default_law": "forbidden", "binding_phase": "semantic_closure" if name in DECISION_NAMES[:70] else "physical_or_deployment_binding",
        "authority_ref": "authority.model_owner_or_vertical_policy",
        "constraints": ["Value is typed, versioned and supported by evidence appropriate to the target and deployment."],
        "invalidation": "A semantic value change invalidates downstream plans, fitted artifacts, evaluations and qualification receipts.",
        "refusals": ["missing", "ambiguous", "unauthorized", "unsupported", "conflicting_precedence"],
    })


PREDICTIVE_LIBRARY_OWNER = {
    **{key: "context.predictive.study_contract" for key in (
        "target_contracts", "label_contracts", "feature_contracts", "split_planner",
        "leakage_guard", "sampling_weights", "weak_supervision",
    )},
    **{key: "context.predictive.model_family_contract" for key in (
        "regression_models", "classification_models", "count_models", "tree_models",
        "kernel_models", "probabilistic_models", "survival_models", "longitudinal_models",
        "forecast_models", "ranking_models", "recommender_models", "graph_models",
        "process_prediction_models", "spatial_models", "online_models",
        "causal_effect_learners", "interpretable_models", "neural_predictive_models",
    )},
    **{key: "context.predictive.algorithm_contract" for key in (
        "objective_functions", "optimizers", "linear_solvers", "factorization_kernels",
        "tree_training_kernels", "tree_inference_kernels", "kernel_matrix_ops",
        "neighbor_search", "graph_sampling", "graph_message_passing", "sequence_kernels",
        "tensor_autodiff", "signal_features", "image_features",
    )},
    **{key: "context.predictive.evaluation_assurance" for key in (
        "calibration", "conformal_prediction", "metrics", "fairness_evaluation",
        "robustness_evaluation", "explanation", "model_selection",
    )},
    **{key: "context.predictive.artifact_identity" for key in (
        "artifact_manifest", "model_serialization",
    )},
    "model_registry_port": "context.predictive.artifact_registry_port",
    **{key: "context.predictive.scoring_execution" for key in (
        "batch_scoring", "online_scoring", "stream_scoring",
    )},
    **{key: "context.predictive.lifecycle_governance" for key in (
        "monitoring", "drift_response", "model_lifecycle",
    )},
    **{key: "context.predictive.provider_binding" for key in (
        "provider_adapter_sklearn", "provider_adapter_statsmodels", "provider_adapter_xgboost",
        "provider_adapter_onnx", "provider_adapter_torch",
    )},
}

PREDICTIVE_LAYER_CLASS = {
    "semantic": "semantic_pure", "method": "semantic_pure", "planning": "policy_pure",
    "validation": "test_oracle", "algorithm": "algorithm_pure", "kernel": "algorithm_pure",
    "evaluation": "test_oracle", "artifact": "semantic_pure",
    "integration": "effect_port_contract", "runtime": "runtime_mechanism",
    "policy": "policy_pure", "adapter": "provider_adapter",
}

PREDICTIVE_LAYER_EFFECT = {
    "integration": "pure_effect_intents", "runtime": "effectful_runtime",
    "adapter": "effectful_runtime",
}

LIBRARIES = []
for key, layer, responsibility in LIBRARY_SPECS:
    LIBRARIES.append({
        "library_id": f"library.predictive.{key}", "edition": EDITION, "layer": layer,
        "semantic_owner_context": PREDICTIVE_LIBRARY_OWNER[key],
        "library_kind": PREDICTIVE_LAYER_CLASS[layer],
        "effect_boundary": PREDICTIVE_LAYER_EFFECT.get(layer, "pure_no_io"),
        "responsibility": responsibility,
        "public_contract": "Provider-neutral typed input/output/error API with all semantic and operational decisions passed explicitly.",
        "purity": "pure" if layer in {"semantic", "method", "planning", "algorithm", "evaluation", "kernel"} else "effect_boundary_explicit",
        "owned_decisions": [d["decision_id"] for d in DECISIONS if key.split("_")[0] in d["decision_id"]][:5],
        "dependencies": [],
        "allowed_dependency_kinds": ["editioned library contribution", "typed canonical reference"],
        "prohibited_dependencies": ["product UI", "hidden global configuration", "unqualified provider occurrence", "LLM/generative agent semantics"],
        "removal_seam": "Trait/port plus conformance fixtures permits replacement without changing domain semantics.",
        "failure_contract": ["invalid_input", "unsupported", "unqualified_provider", "budget_exhausted", "cancelled", "partial"],
        "gaps": ["Concrete Rust crate/API and two independent conforming implementations remain future work."],
    })


REPRESENTATIONS = []
for group, contract in GROUP_CONTRACTS.items():
    REPRESENTATIONS.append({
        "requirement_id": f"representation_requirement.predictive.{group}", "edition": EDITION,
        "model_family_refs": [m["model_family_id"] for m in MODELS if m["family"] == group],
        "semantic_input": contract[1],
        "required_qualifiers": ["entity identity and grain", "valid/recorded/available time", "label and feature definitions", "units/support/CRS/language as applicable", "missing/censoring/unknown states", "provenance and observation cutoff"],
        "acceptable_representations": ["Arrow-like typed tabular batch", "sparse matrix with feature dictionary", "typed tensor with axes", "time-indexed series", "typed static/temporal graph", "event/object graph or trace projection"],
        "transform_laws": ["loss, ordering, null, time and identity semantics are declared", "train and serving transforms are version-identical", "lossy projection emits an explicit information-loss claim"],
        "invalid_inferences": ["unstructured means structure-free", "row order implies event time", "missing interaction means negative label", "latest dimension value was known historically", "graph flattening preserves object interactions"],
    })


QUALIFICATIONS = []
for lib in LIBRARIES:
    QUALIFICATIONS.append({
        "qualification_profile_id": lib["library_id"].replace("library.", "qualification_profile."),
        "edition": EDITION, "library_ref": lib["library_id"], "status": "unexecuted_template",
        "required_evidence": ["exact artifact/version/dependency digest", "target/OS/architecture/device profile", "semantic law and negative-twin tests", "numeric/determinism tests", "resource/cancellation tests", "serialization/upgrade tests", "two unrelated vertical fixtures"],
        "prohibited_claims": ["documentation equals conformance", "benchmark win equals universal superiority", "package installed equals capability bound"],
        "receipt_states": ["passed", "failed", "partial", "unsupported", "not_run", "expired"],
    })


# Artifact-linked experts: authors are evidence-linked to exact artifacts, never ranked or
# declared universally authoritative. Keep the first artifact link for every distinct person.
expert_sources: dict[str, list[str]] = defaultdict(list)
source_by_id = {source["source_id"]: source for source in SOURCES}
for source in SOURCES:
    for author in source["authors"]:
        expert_sources[author].append(source["source_id"])
EXPERTS = []
for name, refs in sorted(expert_sources.items()):
    EXPERTS.append({
        "expert_id": f"expert.predictive.{slug(name)}", "edition": EDITION, "name": name,
        "artifact_refs": sorted(set(refs)),
        "learnable_contributions": [source_by_id[ref]["authority_scope"] for ref in sorted(set(refs))],
        "study_instruction": "Study the exact definitions, assumptions, algorithms, evaluation protocol and limitations in the linked primary artifacts.",
        "authority_law": "Authorship establishes artifact attribution, not universal authority, endorsement, availability or superiority.",
        "verification": "artifact_author_metadata",
    })


ATTRIBUTION_EDGES = []
for expert in EXPERTS:
    for ref in expert["artifact_refs"]:
        ATTRIBUTION_EDGES.append({"edge_id": f"edge.{slug(expert['expert_id'])}.{slug(ref)}", "from_ref": expert["expert_id"], "relation": "authored_or_coauthored", "to_ref": ref, "evidence_ref": ref})


INNOVATIONS = []
for key, year, source_key, contribution, limitation in INNOVATION_SPECS:
    INNOVATIONS.append({
        "innovation_id": f"innovation.predictive.{key}", "edition": EDITION, "year": year,
        "contribution": contribution, "source_refs": [f"source.predictive.{source_key}"],
        "non_llm_core": True, "claim_strength": "artifact_scoped_candidate",
        "limitations": [limitation, "Independent vertical replication and provider qualification remain required."],
    })


VERTICAL_EXAMPLES = [
    {
        "example_id": "vertical_example.predictive.bank_counterparty_default", "vertical": "banking",
        "target": "counterparty default or migration within an explicit horizon", "method_candidates": ["predictive_model.classification.binary_logistic_regression", "predictive_model.tree_ensemble.gradient_boosted_classification_trees", "predictive_model.survival_event_history.cox_proportional_hazards"],
        "required_semantics": ["counterparty and legal-entity identity", "rating/default definition", "as-of and availability time", "right censoring", "economic-cycle split", "exposure and decision-cost policy"],
        "negative_twin_ref": "negative_twin.predictive.bank_random_row_split",
    },
    {
        "example_id": "vertical_example.predictive.hospital_deterioration", "vertical": "acute_care",
        "target": "deterioration event within a declared horizon after observation cutoff", "method_candidates": ["predictive_model.classification.binary_logistic_regression", "predictive_model.longitudinal_panel.generalized_linear_mixed_model", "predictive_model.survival_event_history.landmark_dynamic_prediction"],
        "required_semantics": ["patient/encounter identity", "clinical event-time versus charted-time", "intervention leakage", "competing discharge/death", "site external validation", "calibration and alert workload"],
        "negative_twin_ref": "negative_twin.predictive.health_post_outcome_leakage",
    },
    {
        "example_id": "vertical_example.predictive.manufacturing_failure", "vertical": "manufacturing",
        "target": "asset failure or remaining useful life", "method_candidates": ["predictive_model.survival_event_history.weibull_accelerated_failure_time", "predictive_model.image_signal.fault_diagnosis_vibration_classifier", "predictive_model.anomaly_change.matrix_profile_discord"],
        "required_semantics": ["asset/component identity", "sensor calibration and sample clock", "maintenance intervention", "right censoring", "operating regime", "false-negative/false-positive cost"],
        "negative_twin_ref": "negative_twin.predictive.asset_maintenance_leakage",
    },
    {
        "example_id": "vertical_example.predictive.order_fulfillment", "vertical": "commerce_logistics",
        "target": "remaining time or late-delivery risk across interacting order/item/package objects", "method_candidates": ["predictive_model.process_prediction.heterogeneous_object_event_graph_predictor", "predictive_model.process_prediction.state_aware_ocel_predictor", "predictive_model.process_prediction.trace_prefix_remaining_time_regressor"],
        "required_semantics": ["OCEL/OCED object/event/relation identity", "temporal object state", "observation cutoff", "case projection", "future-event leakage", "object-interaction retention"],
        "negative_twin_ref": "negative_twin.predictive.ocel_flattening",
    },
]


NEGATIVE_TWINS = [
    {"negative_twin_id": "negative_twin.predictive.bank_random_row_split", "invalid_plan": "Randomly split facility-month rows for a counterparty target.", "failure": "The same counterparty and future cycle information leak across partitions.", "required_refusal": "leakage_detected", "repair": "Group by counterparty and use out-of-time evaluation with label-maturity lag."},
    {"negative_twin_id": "negative_twin.predictive.health_post_outcome_leakage", "invalid_plan": "Use chart values recorded after deterioration but backdated to clinical time.", "failure": "Recorded/available time violates the observation cutoff.", "required_refusal": "leakage_detected", "repair": "Point-in-time feature join on actual availability and external site validation."},
    {"negative_twin_id": "negative_twin.predictive.asset_maintenance_leakage", "invalid_plan": "Use post-maintenance sensor signatures to predict the preceding failure.", "failure": "Intervention and outcome consequences enter features.", "required_refusal": "leakage_detected", "repair": "Bind feature availability to prediction origin and model intervention/censoring."},
    {"negative_twin_id": "negative_twin.predictive.ocel_flattening", "invalid_plan": "Flatten every object-centric event to one order case and call it lossless.", "failure": "Many-to-many object interactions, relationship qualifiers and temporal state are duplicated or lost.", "required_refusal": "representation_information_loss_unacknowledged", "repair": "Retain OCEL/OCED graph, bind a declared case projection, or use HOEG/tEKG/state-aware representation under qualification."},
    {"negative_twin_id": "negative_twin.predictive.causal_fit_equals_identification", "invalid_plan": "Select the best treatment-effect predictor by test error and claim causal effect.", "failure": "Predictive evaluation cannot prove exchangeability, positivity, consistency or interference assumptions.", "required_refusal": "not_identified", "repair": "Reference an authorized study/causal identification artifact and run sensitivity/refutation checks."},
    {"negative_twin_id": "negative_twin.predictive.conformal_universal_coverage", "invalid_plan": "Promise per-case coverage under arbitrary deployment shift from an IID split-conformal result.", "failure": "Finite-sample marginal coverage assumptions and scope were strengthened.", "required_refusal": "assumptions_unmet", "repair": "Bind exchangeability/shift model, score, calibration window, group policy and monitoring."},
]


GAPS = [
    {"gap_id": "gap.predictive.open_world", "severity": "constitutional", "description": "The universe is open; no fixed list proves all future predictive methods, targets or representations are covered.", "closure_evidence": ["new primary artifacts", "schema-valid records", "independent audit"]},
    {"gap_id": "gap.predictive.family_specific_theorems", "severity": "high", "description": "Candidate contracts do not yet encode every theorem precondition and finite-sample guarantee for every method variant.", "closure_evidence": ["theorem-level source extraction", "machine-checkable assumption predicates"]},
    {"gap_id": "gap.predictive.provider_qualification", "severity": "high", "description": "Qualification profiles are templates; no deployed package/version/target receives a pass from this corpus.", "closure_evidence": ["executed receipts", "independent implementation comparison"]},
    {"gap_id": "gap.predictive.vertical_binding", "severity": "high", "description": "Four examples are falsification pilots, not complete industry applicability matrices.", "closure_evidence": ["industry case bindings", "domain-owner adjudication"]},
    {"gap_id": "gap.predictive.expert_coverage", "severity": "medium", "description": "Experts are artifact-linked authors, not an exhaustive or ranked social directory.", "closure_evidence": ["ORCID/affiliation verification", "additional primary artifacts"]},
    {"gap_id": "gap.predictive.innovation_window", "severity": "medium", "description": "Innovation records are artifact-scoped candidates; publication date and benchmark result do not establish production value.", "closure_evidence": ["replication", "operational adoption evidence", "failure reports"]},
    {"gap_id": "gap.predictive.generative_boundary", "severity": "medium", "description": "Some predictive architectures use autoregressive or pretraining mechanics; generative product/agent semantics remain quarantined and require separate modeling.", "closure_evidence": ["explicit use-mode classification", "output contract audit"]},
    {"gap_id": "gap.predictive.fairness_law", "severity": "high", "description": "Metric conflicts, local legal authority and harmed-party review cannot be resolved by a generic model family.", "closure_evidence": ["vertical policy", "stakeholder authority", "impact evidence"]},
    {"gap_id": "gap.predictive.resource_benchmarks", "severity": "medium", "description": "Complexity is contractually required but exact resource envelopes remain provider/shape/target measurements.", "closure_evidence": ["qualification benchmarks", "budget-failure tests"]},
]

for rows in (ATTRIBUTION_EDGES, VERTICAL_EXAMPLES, NEGATIVE_TWINS, GAPS):
    for row in rows:
        row.setdefault("edition", EDITION)


SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "urn:san:predictive-ml:record:1",
    "title": "Predictive ML corpus record", "type": "object",
    "required": ["edition"], "properties": {"edition": {"const": 1}},
    "anyOf": [{"required": [key]} for key in ["model_family_id", "component_id", "edge_id", "evidence_edge_id", "operation_id", "decision_id", "library_id", "source_id", "expert_id", "innovation_id", "mapping_id", "requirement_id", "qualification_profile_id", "example_id", "negative_twin_id", "gap_id"]],
    "additionalProperties": True,
}


def main() -> None:
    write_jsonl("sources.jsonl", SOURCES)
    write_jsonl("model-families.jsonl", MODELS)
    write_jsonl("predictive-components.jsonl", COMPONENT_GRAPH)
    write_jsonl("component-edges.jsonl", COMPONENT_EDGES)
    write_jsonl("evidence-edges.jsonl", EVIDENCE_EDGES)
    write_jsonl("operations.jsonl", OPERATIONS)
    write_jsonl("decision-points.jsonl", DECISIONS)
    write_jsonl("library-boundaries.jsonl", LIBRARIES)
    write_jsonl("compiler-mappings.jsonl", MAPPINGS)
    write_jsonl("representation-input-requirements.jsonl", REPRESENTATIONS)
    write_jsonl("provider-qualification-profiles.jsonl", QUALIFICATIONS)
    write_jsonl("experts.jsonl", EXPERTS)
    write_jsonl("expert-artifact-links.jsonl", ATTRIBUTION_EDGES)
    write_jsonl("innovations-2021-2026.jsonl", INNOVATIONS)
    write_jsonl("vertical-examples.jsonl", VERTICAL_EXAMPLES)
    write_jsonl("negative-twins.jsonl", NEGATIVE_TWINS)
    write_jsonl("gaps.jsonl", GAPS)
    write_json("classification-axes.json", TAXONOMY_AXES)
    write_json("corpus-record.schema.json", SCHEMA)
    counts = {
        "sources": len(SOURCES), "model_families": len(MODELS), "operations": len(OPERATIONS),
        "decision_points": len(DECISIONS), "library_boundaries": len(LIBRARIES),
        "experts": len(EXPERTS), "attribution_edges": len(ATTRIBUTION_EDGES),
        "innovations_2021_2026": len(INNOVATIONS), "vertical_examples": len(VERTICAL_EXAMPLES),
        "negative_twins": len(NEGATIVE_TWINS), "representation_requirements": len(REPRESENTATIONS),
        "qualification_profiles": len(QUALIFICATIONS), "compiler_mappings": len(MAPPINGS),
        "predictive_components": len(COMPONENT_GRAPH), "component_edges": len(COMPONENT_EDGES),
        "model_evidence_edges": len(EVIDENCE_EDGES), "taxonomy_axes": len(TAXONOMY_AXES["axes"]),
    }
    manifest = {
        "corpus_id": "universe.predictive_ml_models", "edition": EDITION,
        "status": "researched_candidate_open_world", "completion_claim": False,
        "scope": "Non-generative predictive analytics and statistical machine learning from declared target through monitored deployment.",
        "exclusions": ["LLM application semantics", "generative-agent orchestration", "unscoped benchmark rankings", "causal claims without identification"],
        "counts": counts,
        "field_coverage": dict(sorted(Counter(m["family"] for m in MODELS).items())),
        "minimum_quotas": {"sources": 140, "model_families": 300, "operations": 500, "decision_points": 100, "library_boundaries": 50, "experts": 80, "innovations_2021_2026": 30},
        "content_digest": hashlib.sha256(json.dumps({"counts": counts, "models": [m["model_family_id"] for m in MODELS], "sources": [s["source_id"] for s in SOURCES]}, sort_keys=True).encode()).hexdigest(),
        "generated_at": ACCESSED,
    }
    write_json("manifest.json", manifest)


if __name__ == "__main__":
    main()
