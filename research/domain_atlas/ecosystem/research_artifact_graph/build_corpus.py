#!/usr/bin/env python3
"""Build the governed research-artifact candidate graph deterministically.

This source intentionally keeps publication identity separate from concepts, claims,
methods, algorithms, implementations, benchmarks, and people.  It is a candidate
registry: records not deeply extracted are queued for adjudication rather than being
silently promoted into compiler truth.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AS_OF = "2026-08-25"
RECENT_FROM = 2021


def slug(value: str) -> str:
    out = "".join(c.lower() if c.isalnum() else "_" for c in value)
    return "_".join(filter(None, out.split("_")))


def stable_id(prefix: str, value: str) -> str:
    return f"{prefix}.{slug(value)[:72]}.{hashlib.sha256(value.encode()).hexdigest()[:10]}"


def write_json(path: str, value: object) -> None:
    (ROOT / path).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def write_jsonl(path: str, rows: list[dict]) -> None:
    ordered = sorted(rows, key=lambda x: x["id"])
    (ROOT / path).write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in ordered))


def A(category, key, year, title, url, venue, authors, *, kind="paper", deep=False,
      foundational=None, version="version_of_record_or_cited_edition"):
    if foundational is None:
        foundational = year <= 2020
    return {
        "id": f"artifact.{key}", "key": key, "kind": kind, "category": category, "year": year,
        "title": title, "primary_url": url, "venue": venue, "authors": authors,
        "version": version, "foundational": foundational, "recent": year >= RECENT_FROM,
        "deep": deep,
    }


# Primary research artifacts and standards. Metadata-only records remain candidates and are
# deliberately queued below; their presence is coverage evidence, not endorsement or priority.
ARTIFACTS = [
    # Database, query processing, and transactions.
    A("database_query_transaction", "codd_relational_1970", 1970, "A Relational Model of Data for Large Shared Data Banks", "https://doi.org/10.1145/362384.362685", "Communications of the ACM", ["Edgar F. Codd"], deep=True),
    A("database_query_transaction", "selinger_access_paths_1979", 1979, "Access Path Selection in a Relational Database Management System", "https://doi.org/10.1145/582095.582099", "SIGMOD", ["Patricia G. Selinger", "Morton M. Astrahan", "Donald D. Chamberlin", "Raymond A. Lorie", "Thomas G. Price"], deep=True),
    A("database_query_transaction", "aries_1992", 1992, "ARIES: A Transaction Recovery Method Supporting Fine-Granularity Locking and Partial Rollbacks Using Write-Ahead Logging", "https://doi.org/10.1145/128765.128770", "ACM Transactions on Database Systems", ["C. Mohan", "Don Haderle", "Bruce Lindsay", "Hamid Pirahesh", "Peter Schwarz"]),
    A("database_query_transaction", "volcano_1990", 1990, "Volcano—An Extensible and Parallel Query Evaluation System", "https://doi.org/10.1109/69.58802", "IEEE Transactions on Knowledge and Data Engineering", ["Goetz Graefe"]),
    A("database_query_transaction", "x100_2005", 2005, "MonetDB/X100: Hyper-Pipelining Query Execution", "https://www.cidrdb.org/cidr2005/papers/P19.pdf", "CIDR", ["Peter Boncz", "Marcin Zukowski", "Niels Nes"]),
    A("database_query_transaction", "dremel_2010", 2010, "Dremel: Interactive Analysis of Web-Scale Datasets", "https://research.google/pubs/dremel-interactive-analysis-of-web-scale-datasets-2/", "VLDB", ["Sergey Melnik", "Andrey Gubarev", "Jing Jing Long", "Geoffrey Romer", "Shiva Shivakumar", "Matt Tolton", "Theo Vassilakis"]),
    A("database_query_transaction", "spanner_2012", 2012, "Spanner: Google's Globally-Distributed Database", "https://research.google/pubs/spanner-googles-globally-distributed-database/", "OSDI", ["James C. Corbett", "Jeffrey Dean", "Michael Epstein", "Andrew Fikes", "Christopher Frost", "J. J. Furman", "Sanjay Ghemawat", "Andrey Gubarev", "Christopher Heiser", "Peter Hochschild", "Wilson Hsieh", "Sebastian Kanthak", "Eugene Kogan", "Hongyi Li", "Alexander Lloyd", "Sergey Melnik", "David Mwaura", "David Nagle", "Sean Quinlan", "Rajesh Rao", "Lindsay Rolig", "Yasushi Saito", "Michal Szymaniak", "Christopher Taylor", "Ruth Wang", "Dale Woodford"]),
    A("database_query_transaction", "duckdb_2019", 2019, "DuckDB: An Embeddable Analytical Database", "https://doi.org/10.1145/3299869.3320212", "SIGMOD", ["Mark Raasveldt", "Hannes Mühleisen"]),
    A("database_query_transaction", "lakehouse_2021", 2021, "Lakehouse: A New Generation of Open Platforms that Unify Data Warehousing and Advanced Analytics", "https://www.cidrdb.org/cidr2021/papers/cidr2021_paper17.pdf", "CIDR", ["Michael Armbrust", "Ali Ghodsi", "Reynold Xin", "Matei Zaharia"], deep=True),
    A("database_query_transaction", "bao_2021", 2021, "Bao: Making Learned Query Optimization Practical", "https://doi.org/10.1145/3448016.3452838", "SIGMOD", ["Ryan Marcus", "Parimarjan Negi", "Hongzi Mao", "Nesime Tatbul", "Mohammad Alizadeh", "Tim Kraska"]),
    A("database_query_transaction", "velox_2022", 2022, "Velox: Meta's Unified Execution Engine", "https://www.vldb.org/pvldb/vol15/p3372-pedreira.pdf", "PVLDB", ["Pedro Pedreira", "Orri Erling", "Masha Basmanova", "Kevin Wilfong", "Laith Sakka", "Krishna Pai", "Wei He", "Biswapesh Chattopadhyay"]),
    A("database_query_transaction", "tqp_plus_plus_2026", 2026, "TQP++: Bridging ML Compilers and Analytical Query Processing on GPUs", "https://www.microsoft.com/en-us/research/publication/tqp-bridging-ml-compilers-and-analytical-query-processing-on-gpus/", "VLDB 2026 Industrial Track", ["Wei Cui", "Peng Cheng", "Carlo Curino", "Rathijit Sen", "Matteo Interlandi"], kind="preprint", deep=True),

    # Distributed systems, streams, and dataflow.
    A("distributed_streaming", "chandy_lamport_1985", 1985, "Distributed Snapshots: Determining Global States of Distributed Systems", "https://doi.org/10.1145/214451.214456", "ACM Transactions on Computer Systems", ["K. Mani Chandy", "Leslie Lamport"], deep=True),
    A("distributed_streaming", "mapreduce_2004", 2004, "MapReduce: Simplified Data Processing on Large Clusters", "https://research.google/pubs/mapreduce-simplified-data-processing-on-large-clusters/", "OSDI", ["Jeffrey Dean", "Sanjay Ghemawat"]),
    A("distributed_streaming", "dynamo_2007", 2007, "Dynamo: Amazon's Highly Available Key-value Store", "https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf", "SOSP", ["Giuseppe DeCandia", "Deniz Hastorun", "Madan Jampani", "Gunavardhan Kakulapati", "Avinash Lakshman", "Alex Pilchin", "Swaminathan Sivasubramanian", "Peter Vosshall", "Werner Vogels"]),
    A("distributed_streaming", "kafka_2011", 2011, "Kafka: A Distributed Messaging System for Log Processing", "https://notes.stephenholiday.com/Kafka.pdf", "NetDB", ["Jay Kreps", "Neha Narkhede", "Jun Rao"]),
    A("distributed_streaming", "naiad_2013", 2013, "Naiad: A Timely Dataflow System", "https://doi.org/10.1145/2517349.2522738", "SOSP", ["Derek G. Murray", "Frank McSherry", "Rebecca Isaacs", "Michael Isard", "Paul Barham", "Martín Abadi"]),
    A("distributed_streaming", "millwheel_2013", 2013, "MillWheel: Fault-Tolerant Stream Processing at Internet Scale", "https://research.google/pubs/millwheel-fault-tolerant-stream-processing-at-internet-scale/", "VLDB", ["Tyler Akidau", "Alex Balikov", "Kaya Bekiroğlu", "Slava Chernyak", "Josh Haberman", "Reuven Lax", "Sam McVeety", "Daniel Mills", "Paul Nordstrom", "Sam Whittle"]),
    A("distributed_streaming", "dataflow_2015", 2015, "The Dataflow Model: A Practical Approach to Balancing Correctness, Latency, and Cost in Massive-Scale, Unbounded, Out-of-Order Data Processing", "https://research.google/pubs/the-dataflow-model-a-practical-approach-to-balancing-correctness-latency-and-cost-in-massive-scale-unbounded-out-of-order-data-processing/", "VLDB", ["Tyler Akidau", "Robert Bradshaw", "Craig Chambers", "Slava Chernyak", "Rafael Fernández-Moctezuma", "Reuven Lax", "Sam McVeety", "Daniel Mills", "Frances Perry", "Eric Schmidt", "Sam Whittle"], deep=True),
    A("distributed_streaming", "flink_2015", 2015, "Apache Flink: Stream and Batch Processing in a Single Engine", "https://doi.org/10.1109/MC.2015.258", "IEEE Data Engineering Bulletin / IEEE Computer", ["Paris Carbone", "Asterios Katsifodimos", "Stephan Ewen", "Volker Markl", "Seif Haridi", "Kostas Tzoumas"]),
    A("distributed_streaming", "styx_2021", 2021, "Styx: Transactional Stateful Functions on Streaming Dataflows", "https://arxiv.org/abs/2109.10998", "arXiv / distributed systems research artifact", ["Vasiliki Kalavri", "John Liagouris", "Moritz Hoffmann", "Despoina Dimitrova", "Matthew Forshaw", "Tim Roscoe"]),
    A("distributed_streaming", "boki_2021", 2021, "Boki: Stateful Serverless Computing with Shared Logs", "https://doi.org/10.1145/3477132.3483541", "SOSP", ["Zhipeng Jia", "Emmett Witchel"]),
    A("distributed_streaming", "dbos_2023", 2023, "DBOS: A Proposal for a Data-Centric Operating System", "https://www.cidrdb.org/cidr2023/papers/p44-stonebraker.pdf", "CIDR", ["Michael Stonebraker", "Matei Zaharia", "Stan Zdonik", "Tim Kraska", "Jeremy Kepner", "Andy Pavlo"]),

    # Compression, formats, and physical storage.
    A("compression_storage", "huffman_1952", 1952, "A Method for the Construction of Minimum-Redundancy Codes", "https://doi.org/10.1109/JRPROC.1952.273898", "Proceedings of the IRE", ["David A. Huffman"], deep=True),
    A("compression_storage", "lz77_1977", 1977, "A Universal Algorithm for Sequential Data Compression", "https://doi.org/10.1109/TIT.1977.1055714", "IEEE Transactions on Information Theory", ["Jacob Ziv", "Abraham Lempel"]),
    A("compression_storage", "b_tree_1972", 1972, "Organization and Maintenance of Large Ordered Indexes", "https://doi.org/10.1007/BF00288683", "Acta Informatica", ["Rudolf Bayer", "Edward M. McCreight"]),
    A("compression_storage", "gorilla_2015", 2015, "Gorilla: A Fast, Scalable, In-Memory Time Series Database", "https://doi.org/10.14778/2824032.2824078", "PVLDB", ["Tuomas Pelkonen", "Scott Franklin", "Justin Teller", "Paul Cavallaro", "Qi Huang", "Justin Meza", "Kaushik Veeraraghavan"]),
    A("compression_storage", "fsst_2020", 2020, "FSST: Fast Random Access String Compression", "https://www.vldb.org/pvldb/vol13/p2649-boncz.pdf", "PVLDB", ["Peter Boncz", "Thomas Neumann", "Viktor Leis"]),
    A("compression_storage", "zstd_rfc_2021", 2021, "Zstandard Compression and the application/zstd Media Type", "https://www.rfc-editor.org/rfc/rfc8878", "IETF RFC 8878", ["Yann Collet", "Murray Kucherawy"], kind="standard"),
    A("compression_storage", "btrblocks_2023", 2023, "BtrBlocks: Efficient Columnar Compression for Data Lakes", "https://doi.org/10.1145/3589263", "Proceedings of the ACM on Management of Data / SIGMOD", ["Maximilian Kuschewski", "David Sauerwein", "Adnan Alhomssi", "Viktor Leis"], deep=True),
    A("compression_storage", "leco_2024", 2024, "LeCo: Lightweight Compression via Learning Serial Correlations", "https://doi.org/10.1145/3639301", "Proceedings of the ACM on Management of Data / SIGMOD", ["Yihao Liu", "Xinyu Zeng", "Huanchen Zhang"]),
    A("compression_storage", "alp_2023", 2023, "ALP: Adaptive Lossless Floating-Point Compression", "https://doi.org/10.1145/3626717", "Proceedings of the ACM on Management of Data / SIGMOD 2024 program", ["Azim Afroozeh", "Leonardo X. Kuffo", "Peter Boncz"]),
    A("compression_storage", "zarr_v3_2023", 2023, "Zarr Storage Specification Version 3", "https://zarr-specs.readthedocs.io/en/latest/v3/core/v3.0.html", "Zarr specification", ["Zarr specification contributors"], kind="standard"),

    # Programming languages, compilers, and intermediate representations.
    A("programming_languages_compilers", "ssa_1991", 1991, "Efficiently Computing Static Single Assignment Form and the Control Dependence Graph", "https://doi.org/10.1145/115372.115320", "ACM TOPLAS", ["Ron Cytron", "Jeanne Ferrante", "Barry K. Rosen", "Mark N. Wegman", "F. Kenneth Zadeck"], deep=True),
    A("programming_languages_compilers", "llvm_2004", 2004, "LLVM: A Compilation Framework for Lifelong Program Analysis & Transformation", "https://doi.org/10.1109/CGO.2004.1281665", "CGO", ["Chris Lattner", "Vikram Adve"]),
    A("programming_languages_compilers", "sea_of_nodes_1995", 1995, "Combining Analyses, Combining Optimizations", "https://doi.org/10.1145/207110.207154", "PLDI", ["Cliff Click"]),
    A("programming_languages_compilers", "truffle_2013", 2013, "One VM to Rule Them All", "https://doi.org/10.1145/2509578.2509581", "Onward!", ["Thomas Würthinger", "Christian Wimmer", "Andreas Wöß", "Lukas Stadler", "Gilles Duboscq", "Christian Humer", "Gregor Richards", "Doug Simon", "Mario Wolczko"]),
    A("programming_languages_compilers", "weld_2017", 2017, "Weld: Rethinking the Interface Between Data-Intensive Applications", "https://doi.org/10.1145/3035918.3056059", "CIDR / SIGMOD", ["Shoumik Palkar", "James Thomas", "Anil Shanbhag", "Deepak Narayanan", "Holger Pirk", "Malte Schwarzkopf", "Saman Amarasinghe", "Matei Zaharia"]),
    A("programming_languages_compilers", "webassembly_2017", 2017, "Bringing the Web Up to Speed with WebAssembly", "https://doi.org/10.1145/3062341.3062363", "PLDI", ["Andreas Haas", "Andreas Rossberg", "Derek L. Schuff", "Ben L. Titzer", "Michael Holman", "Dan Gohman", "Luke Wagner", "Alon Zakai", "J. F. Bastien"]),
    A("programming_languages_compilers", "rustbelt_2018", 2018, "RustBelt: Securing the Foundations of the Rust Programming Language", "https://doi.org/10.1145/3158154", "POPL", ["Ralf Jung", "Jacques-Henri Jourdan", "Robbert Krebbers", "Derek Dreyer"]),
    A("programming_languages_compilers", "mlir_2021", 2021, "MLIR: Scaling Compiler Infrastructure for Domain Specific Computation", "https://doi.org/10.1109/CGO51591.2021.9370308", "CGO", ["Chris Lattner", "Mehdi Amini", "Uday Bondhugula", "Albert Cohen", "Andy Davis", "Jacques Pienaar", "River Riddle", "Tatiana Shpeisman", "Nicolas Vasilache", "Oleksandr Zinenko"], deep=True),
    A("programming_languages_compilers", "egg_2021", 2021, "egg: Fast and Extensible Equality Saturation", "https://doi.org/10.1145/3434304", "POPL", ["Max Willsey", "Chandrakana Nandi", "Yewen Pu", "Pavel Panchekha", "Zachary Tatlock", "Vikram S. Adve", "Michael Carbin"]),
    A("programming_languages_compilers", "dbsp_2023", 2023, "DBSP: Automatic Incremental View Maintenance for Rich Query Languages", "https://arxiv.org/abs/2203.16684", "VLDB / arXiv", ["Mihai Budiu", "Tej Chajed", "Frank McSherry", "Leonid Ryzhyk", "Val Tannen"]),

    # Information retrieval and nearest-neighbor search.
    A("information_retrieval", "bm25_1994", 1994, "Some Simple Effective Approximations to the 2-Poisson Model for Probabilistic Weighted Retrieval", "https://www.staff.city.ac.uk/~sbrp622/papers/sigir94.pdf", "SIGIR", ["Stephen E. Robertson", "Steve Walker", "Susan Jones", "Micheline Hancock-Beaulieu", "Mike Gatford"], deep=True),
    A("information_retrieval", "pagerank_1999", 1999, "The PageRank Citation Ranking: Bringing Order to the Web", "https://ilpubs.stanford.edu:8090/422/", "Stanford technical report", ["Lawrence Page", "Sergey Brin", "Rajeev Motwani", "Terry Winograd"]),
    A("information_retrieval", "wand_2003", 2003, "Efficient Query Evaluation Using a Two-Level Retrieval Process", "https://doi.org/10.1145/956863.956944", "CIKM", ["Andrei Z. Broder", "David Carmel", "Michael Herscovici", "Aya Soffer", "Jason Zien"]),
    A("information_retrieval", "product_quantization_2011", 2011, "Product Quantization for Nearest Neighbor Search", "https://doi.org/10.1109/TPAMI.2010.57", "IEEE TPAMI", ["Hervé Jégou", "Matthijs Douze", "Cordelia Schmid"]),
    A("information_retrieval", "block_max_wand_2011", 2011, "Faster Top-k Document Retrieval Using Block-Max Indexes", "https://doi.org/10.1145/2009916.2010048", "SIGIR", ["Shuai Ding", "Josh Attenberg", "Torsten Suel"]),
    A("information_retrieval", "hnsw_2016", 2016, "Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs", "https://doi.org/10.1109/TPAMI.2018.2889473", "IEEE TPAMI", ["Yu. A. Malkov", "D. A. Yashunin"], deep=True),
    A("information_retrieval", "faiss_2017", 2017, "Billion-Scale Similarity Search with GPUs", "https://arxiv.org/abs/1702.08734", "IEEE BigData / arXiv", ["Jeff Johnson", "Matthijs Douze", "Hervé Jégou"]),
    A("information_retrieval", "scann_2020", 2020, "Accelerating Large-Scale Inference with Anisotropic Vector Quantization", "https://proceedings.mlr.press/v119/guo20h.html", "ICML", ["Ruiqi Guo", "Philip Sun", "Erik Lindgren", "Quan Geng", "David Simcha", "Felix Chern", "Sanjiv Kumar"]),
    A("information_retrieval", "spann_2021", 2021, "SPANN: Highly-efficient Billion-scale Approximate Nearest Neighbor Search", "https://proceedings.neurips.cc/paper/2021/hash/18fdcc041db0d9f2f0de6a8b55b09c0f-Abstract.html", "NeurIPS", ["Qi Chen", "Bing Zhao", "Haidong Wang", "Mingqin Li", "Chuanjie Liu", "Zengzhong Li", "Mao Yang", "Jingdong Wang"]),
    A("information_retrieval", "ann_benchmarks_2021", 2021, "ANN-Benchmarks: A Benchmarking Tool for Approximate Nearest Neighbor Algorithms", "https://doi.org/10.1016/j.is.2021.101682", "Information Systems", ["Martin Aumüller", "Erik Bernhardsson", "Alexander Faithfull"], deep=True),

    # Visualization, interactive analysis, and HCI.
    A("visualization_hci", "cleveland_mcgill_1984", 1984, "Graphical Perception: Theory, Experimentation, and Application to the Development of Graphical Methods", "https://doi.org/10.1080/01621459.1984.10478080", "JASA", ["William S. Cleveland", "Robert McGill"], deep=True),
    A("visualization_hci", "mackinlay_1986", 1986, "Automating the Design of Graphical Presentations of Relational Information", "https://doi.org/10.1145/22949.22950", "ACM TOG", ["Jock D. Mackinlay"]),
    A("visualization_hci", "polaris_2002", 2002, "Polaris: A System for Query, Analysis, and Visualization of Multidimensional Relational Databases", "https://doi.org/10.1109/TVCG.2002.1021575", "IEEE TVCG", ["Chris Stolte", "Diane Tang", "Pat Hanrahan"]),
    A("visualization_hci", "d3_2011", 2011, "D3: Data-Driven Documents", "https://doi.org/10.1109/TVCG.2011.185", "IEEE TVCG", ["Michael Bostock", "Vadim Ogievetsky", "Jeffrey Heer"]),
    A("visualization_hci", "wrangler_2011", 2011, "Wrangler: Interactive Visual Specification of Data Transformation Scripts", "https://doi.org/10.1145/1978942.1979444", "CHI", ["Sean Kandel", "Andreas Paepcke", "Joseph Hellerstein", "Jeffrey Heer"]),
    A("visualization_hci", "vega_lite_2017", 2017, "Vega-Lite: A Grammar of Interactive Graphics", "https://doi.org/10.1109/TVCG.2016.2599030", "IEEE TVCG", ["Arvind Satyanarayan", "Dominik Moritz", "Kanitra Wongsuphasawat", "Jeffrey Heer"], deep=True),
    A("visualization_hci", "draco_2018", 2018, "Formalizing Visualization Design Knowledge as Constraints: Actionable and Extensible Models in Draco", "https://doi.org/10.1109/TVCG.2018.2865240", "IEEE TVCG", ["Dominik Moritz", "Chenglong Wang", "Greg L. Nelson", "Halden Lin", "Adam M. Smith", "Bill Howe", "Jeffrey Heer"]),
    A("visualization_hci", "falcon_2019", 2019, "Falcon: Balancing Interactive Latency and Resolution Sensitivity for Scalable Linked Visualizations", "https://doi.org/10.1145/3290605.3300924", "CHI", ["Dominik Moritz", "Bill Howe", "Jeffrey Heer"]),
    A("visualization_hci", "arquero_2021", 2021, "Arquero: Manipulating Tabular Data with JavaScript", "https://idl.cs.washington.edu/files/2021-Arquero-UIST.pdf", "UIST", ["Jeffrey Heer"]),
    A("visualization_hci", "mosaic_2023", 2023, "Mosaic: An Architecture for Scalable and Interoperable Data Views", "https://idl.cs.washington.edu/papers/mosaic/", "IEEE VIS / TVCG", ["Jeffrey Heer", "Dominik Moritz"], deep=True),

    # Statistics, causal inference, and non-LLM predictive analytics.
    A("statistics_ml_predictive", "kalman_1960", 1960, "A New Approach to Linear Filtering and Prediction Problems", "https://doi.org/10.1115/1.3662552", "Journal of Basic Engineering", ["Rudolf E. Kalman"], deep=True),
    A("statistics_ml_predictive", "cox_1972", 1972, "Regression Models and Life-Tables", "https://doi.org/10.1111/j.2517-6161.1972.tb00899.x", "JRSS Series B", ["David R. Cox"]),
    A("statistics_ml_predictive", "gradient_boosting_2001", 2001, "Greedy Function Approximation: A Gradient Boosting Machine", "https://doi.org/10.1214/aos/1013203451", "Annals of Statistics", ["Jerome H. Friedman"]),
    A("statistics_ml_predictive", "random_forests_2001", 2001, "Random Forests", "https://doi.org/10.1023/A:1010933404324", "Machine Learning", ["Leo Breiman"]),
    A("statistics_ml_predictive", "conformal_prediction_2005", 2005, "Algorithmic Learning in a Random World", "https://link.springer.com/book/10.1007/b106715", "Springer monograph", ["Vladimir Vovk", "Alexander Gammerman", "Glenn Shafer"], kind="book", deep=True),
    A("statistics_ml_predictive", "xgboost_2016", 2016, "XGBoost: A Scalable Tree Boosting System", "https://doi.org/10.1145/2939672.2939785", "KDD", ["Tianqi Chen", "Carlos Guestrin"], deep=True),
    A("statistics_ml_predictive", "lightgbm_2017", 2017, "LightGBM: A Highly Efficient Gradient Boosting Decision Tree", "https://proceedings.neurips.cc/paper/2017/hash/6449f44a102fde848669bdd9eb6b76fa-Abstract.html", "NeurIPS", ["Guolin Ke", "Qi Meng", "Thomas Finley", "Taifeng Wang", "Wei Chen", "Weidong Ma", "Qiwei Ye", "Tie-Yan Liu"]),
    A("statistics_ml_predictive", "double_ml_2018", 2018, "Double/Debiased Machine Learning for Treatment and Structural Parameters", "https://doi.org/10.1111/ectj.12097", "Econometrics Journal", ["Victor Chernozhukov", "Denis Chetverikov", "Mert Demirer", "Esther Duflo", "Christian Hansen", "Whitney Newey", "James Robins"], deep=True),
    A("statistics_ml_predictive", "nhits_2022", 2022, "N-HiTS: Neural Hierarchical Interpolation for Time Series Forecasting", "https://ojs.aaai.org/index.php/AAAI/article/view/20590", "AAAI", ["Cristian Challu", "Kin G. Olivares", "Boris N. Oreshkin", "Federico Garza", "Max Mergenthaler-Canseco", "Artur Dubrawski"]),
    A("statistics_ml_predictive", "patchtst_2023", 2023, "A Time Series is Worth 64 Words: Long-term Forecasting with Transformers", "https://openreview.net/forum?id=Jbdc0vTOcol", "ICLR", ["Yuqi Nie", "Nam H. Nguyen", "Phanwadee Sinthong", "Jayant Kalagnanam"], deep=True),
    A("statistics_ml_predictive", "conformal_time_series_2021", 2021, "Conformal Prediction Interval for Dynamic Time-Series", "https://proceedings.mlr.press/v139/xu21h.html", "ICML", ["Chen Xu", "Yao Xie"]),

    # Process mining, object-centric event data, and process prediction.
    A("process_mining", "alpha_miner_2004", 2004, "Workflow Mining: Discovering Process Models from Event Logs", "https://doi.org/10.1109/TKDE.2004.47", "IEEE TKDE", ["Wil M. P. van der Aalst", "Ton Weijters", "Laura Maruster"]),
    A("process_mining", "heuristics_miner_2006", 2006, "Process Mining with the HeuristicsMiner Algorithm", "https://research.tue.nl/en/publications/process-mining-with-the-heuristicsminer-algorithm", "BETA working paper", ["A. J. M. M. Weijters", "Wil M. P. van der Aalst", "Ana Karla Alves de Medeiros"]),
    A("process_mining", "alignments_2012", 2012, "Process Conformance Using Alignments", "https://doi.org/10.1007/978-3-642-36285-9_9", "BPM", ["Arya Adriansyah", "Boudewijn van Dongen", "Wil M. P. van der Aalst"]),
    A("process_mining", "inductive_miner_2013", 2013, "Discovering Block-Structured Process Models from Event Logs—A Constructive Approach", "https://doi.org/10.1007/978-3-642-38697-8_17", "Petri Nets", ["Sander J. J. Leemans", "Dirk Fahland", "Wil M. P. van der Aalst"], deep=True),
    A("process_mining", "ocpn_2020", 2020, "Object-Centric Process Mining: Dealing with Divergence and Convergence in Event Data", "https://doi.org/10.1007/978-3-030-33246-4_1", "SEFM", ["Wil M. P. van der Aalst", "Guangming Li", "Marco Montali"]),
    A("process_mining", "ekg_dimensions_2022", 2022, "Process Mining over Multiple Behavioral Dimensions with Event Knowledge Graphs", "https://doi.org/10.1007/978-3-031-08848-3_9", "Process Mining Handbook", ["Dirk Fahland"], kind="book_chapter", deep=True),
    A("process_mining", "predictive_ocpm_2022", 2022, "Predictive Object-Centric Process Monitoring", "https://arxiv.org/abs/2207.10017", "Master thesis / arXiv", ["Timo Rohrer", "Anahita Farhang Ghahfarokhi", "Mohamed Behery", "Gerhard Lakemeyer", "Wil M. P. van der Aalst"], kind="thesis", deep=True),
    A("process_mining", "ocel2_2023", 2023, "OCEL (Object-Centric Event Log) 2.0 Specification", "https://www.ocel-standard.org/2.0/ocel20_specification.pdf", "OCEL standard", ["Alessandro Berti", "István Koren", "Jan Niklas Adams", "Gyunam Park", "Benedikt Knopp", "Nina Graves", "Majid Rafiei", "Lukas Liß", "Leah Tacke Genannt Unterberg", "Yisong Zhang", "Christopher Schwanen", "Marco Pegoraro", "Wil M. P. van der Aalst"], kind="standard", deep=True),
    A("process_mining", "oced_pg_2024", 2024, "Implementing Object-Centric Event Data Models in Event Knowledge Graphs", "https://doi.org/10.1007/978-3-031-56107-8_33", "ICPM Workshops", ["Ava Swevels", "Dirk Fahland", "Marco Montali"], deep=True),
    A("process_mining", "oced_core_2024", 2024, "Towards a Simple and Extensible Standard for Object-Centric Event Data: Core Model, Design Space, and Lessons Learned", "https://arxiv.org/abs/2410.14495", "arXiv / OCED working group", ["Dirk Fahland", "Marco Montali", "Julian Lebherz", "Wil M. P. van der Aalst", "OCED working-group contributors; exact list pending"], kind="preprint", deep=True),
    A("process_mining", "tekg_2024", 2024, "Transforming Object-Centric Event Logs to Temporal Event Knowledge Graphs", "https://arxiv.org/abs/2406.07596", "ER / arXiv", ["Shahrzad Khayatbashi", "Olaf Hartig", "Amin Jalali"], deep=True),
    A("process_mining", "sa_ocpm_2026", 2026, "State-Aware Object-Centric Process Mining: Enhancing OCEL 2.0 with Explicit State Transitions", "https://doi.org/10.1007/978-3-032-15140-7_6", "Lecture Notes in Computer Science", ["Dina Kretzschmann", "Alessandro Berti", "Wil M. P. van der Aalst"], deep=True),

    # Graph, spatial, and scientific-array systems.
    A("graph_spatial_scientific", "rtree_1984", 1984, "R-Trees: A Dynamic Index Structure for Spatial Searching", "https://doi.org/10.1145/602259.602266", "SIGMOD", ["Antonin Guttman"], deep=True),
    A("graph_spatial_scientific", "rasdaman_1998", 1998, "RasDaMan: A Multi-Dimensional DBMS", "https://doi.org/10.1145/276305.276386", "SIGMOD", ["Peter Baumann", "Andreas Dehmel", "Paula Furtado", "Roland Ritsch", "Norbert Widmann"]),
    A("graph_spatial_scientific", "scidb_2009", 2009, "Requirements for Science Data Bases and SciDB", "https://www.cidrdb.org/cidr2009/Paper_26.pdf", "CIDR", ["Paul G. Brown"]),
    A("graph_spatial_scientific", "pregel_2010", 2010, "Pregel: A System for Large-Scale Graph Processing", "https://research.google/pubs/pregel-a-system-for-large-scale-graph-processing/", "SIGMOD", ["Grzegorz Malewicz", "Matthew H. Austern", "Aart J. C. Bik", "James C. Dehnert", "Ilan Horn", "Naty Leiser", "Grzegorz Czajkowski"]),
    A("graph_spatial_scientific", "graphx_2014", 2014, "GraphX: Unifying Data-Parallel and Graph-Parallel Analytics", "https://doi.org/10.48550/arXiv.1402.2394", "OSDI / arXiv", ["Reynold S. Xin", "Daniel Crankshaw", "Ankur Dave", "Joseph E. Gonzalez", "Michael J. Franklin", "Ion Stoica"]),
    A("graph_spatial_scientific", "xarray_2017", 2017, "xarray: N-D Labeled Arrays and Datasets in Python", "https://doi.org/10.5334/jors.148", "Journal of Open Research Software", ["Stephan Hoyer", "Joe Hamman"]),
    A("graph_spatial_scientific", "tiledb_2017", 2017, "The TileDB Array Data Storage Manager", "https://doi.org/10.14778/3137765.3137831", "PVLDB", ["Stavros Papadopoulos", "Kostas Datta", "Samuel Madden", "Tim Mattson"]),
    A("graph_spatial_scientific", "graphblas_2017", 2017, "GraphBLAS Mathematics on Directed Graphs", "https://doi.org/10.1109/HPEC.2017.8091096", "HPEC", ["Jeremy Kepner", "Peter Aaltonen", "David Bader", "Aydın Buluç", "Franz Franchetti", "John Gilbert", "Dylan Hutchison", "Manfred Kicherer", "David O'Leary", "Elena Phillips", "Mike Reuther", "Timothy Sheehan", "John Turner", "Jonathan Weale"]),
    A("graph_spatial_scientific", "geoarrow_2022", 2022, "GeoArrow Specification", "https://geoarrow.org/extension-types.html", "GeoArrow specification", ["GeoArrow contributors"], kind="standard"),
    A("graph_spatial_scientific", "geoparquet_2024", 2024, "GeoParquet Specification 1.1.0", "https://geoparquet.org/releases/v1.1.0/", "GeoParquet specification", ["GeoParquet contributors"], kind="standard", deep=True),

    # Operations research, mathematical optimization, and control.
    A("optimization_control", "simplex_1947", 1947, "Maximization of a Linear Function of Variables Subject to Linear Inequalities", "https://doi.org/10.1007/978-1-4613-9060-7_9", "Activity Analysis of Production and Allocation", ["George B. Dantzig"]),
    A("optimization_control", "dynamic_programming_1957", 1957, "Dynamic Programming", "https://press.princeton.edu/books/paperback/9780691146683/dynamic-programming", "Princeton University Press", ["Richard Bellman"], kind="book"),
    A("optimization_control", "branch_bound_1960", 1960, "An Automatic Method of Solving Discrete Programming Problems", "https://doi.org/10.2307/1910129", "Econometrica", ["Ailsa H. Land", "Alison G. Doig"]),
    A("optimization_control", "simulated_annealing_1983", 1983, "Optimization by Simulated Annealing", "https://doi.org/10.1126/science.220.4598.671", "Science", ["Scott Kirkpatrick", "C. Daniel Gelatt", "Mario P. Vecchi"]),
    A("optimization_control", "robust_optimization_2004", 2004, "Robust Optimization", "https://doi.org/10.1287/opre.1030.0087", "Operations Research", ["Aharon Ben-Tal", "Arkadi Nemirovski"]),
    A("optimization_control", "admm_2011", 2011, "Distributed Optimization and Statistical Learning via the Alternating Direction Method of Multipliers", "https://web.stanford.edu/~boyd/papers/admm_distr_stats.html", "Foundations and Trends in Machine Learning", ["Stephen Boyd", "Neal Parikh", "Eric Chu", "Borja Peleato", "Jonathan Eckstein"], deep=True),
    A("optimization_control", "cvxpy_2016", 2016, "CVXPY: A Python-Embedded Modeling Language for Convex Optimization", "https://doi.org/10.1007/s12532-015-0094-0", "Mathematical Programming Computation", ["Steven Diamond", "Stephen Boyd"]),
    A("optimization_control", "osqp_2020", 2020, "OSQP: An Operator Splitting Solver for Quadratic Programs", "https://doi.org/10.1007/s12532-020-00179-2", "Mathematical Programming Computation", ["Bartolomeo Stellato", "Goran Banjac", "Paul Goulart", "Alberto Bemporad", "Stephen Boyd"], deep=True),
    A("optimization_control", "pdlp_2021", 2021, "Practical Large-Scale Linear Programming Using Primal-Dual Hybrid Gradient", "https://arxiv.org/abs/2106.04756", "NeurIPS / arXiv", ["David Applegate", "Mateo Díaz", "Oliver Hinder", "Haihao Lu", "Miles Lubin", "Brendan O'Donoghue", "Warren Schudy"]),
    A("optimization_control", "cp_sat_2023", 2023, "The CP-SAT-LP Solver", "https://doi.org/10.1007/s12532-023-00239-1", "Mathematical Programming Computation", ["Frédéric Didier", "Laurent Perron"], deep=True),

    # Security, privacy, authorization, and software supply-chain evidence.
    A("security_privacy", "bell_lapadula_1973", 1973, "Secure Computer Systems: Mathematical Foundations", "https://csrc.nist.gov/csrc/media/publications/conference-paper/1998/10/08/proceedings-of-the-21st-nissc-1998/documents/early-cs-papers/bell76.pdf", "MITRE technical report", ["David Elliott Bell", "Leonard J. LaPadula"]),
    A("security_privacy", "denning_lattice_1976", 1976, "A Lattice Model of Secure Information Flow", "https://doi.org/10.1145/360051.360056", "Communications of the ACM", ["Dorothy E. Denning"]),
    A("security_privacy", "k_anonymity_2002", 2002, "k-Anonymity: A Model for Protecting Privacy", "https://doi.org/10.1142/S0218488502001648", "International Journal of Uncertainty, Fuzziness and Knowledge-Based Systems", ["Latanya Sweeney"]),
    A("security_privacy", "differential_privacy_2006", 2006, "Calibrating Noise to Sensitivity in Private Data Analysis", "https://doi.org/10.1007/11681878_14", "TCC", ["Cynthia Dwork", "Frank McSherry", "Kobbi Nissim", "Adam Smith"], deep=True),
    A("security_privacy", "l_diversity_2006", 2006, "l-Diversity: Privacy Beyond k-Anonymity", "https://doi.org/10.1145/1217299.1217302", "ACM TKDD", ["Ashwin Machanavajjhala", "Daniel Kifer", "Johannes Gehrke", "Muthuramakrishnan Venkitasubramaniam"]),
    A("security_privacy", "rappor_2014", 2014, "RAPPOR: Randomized Aggregatable Privacy-Preserving Ordinal Response", "https://doi.org/10.1145/2660267.2660348", "CCS", ["Úlfar Erlingsson", "Vasyl Pihur", "Aleksandra Korolova"]),
    A("security_privacy", "macaroons_2014", 2014, "Macaroons: Cookies with Contextual Caveats for Decentralized Authorization in the Cloud", "https://research.google/pubs/macaroons-cookies-with-contextual-caveats-for-decentralized-authorization-in-the-cloud/", "NDSS", ["Arnar Birgisson", "Joe Gibbs Politz", "Úlfar Erlingsson", "Ankur Taly", "Michael Vrable", "Mark Lentczner"]),
    A("security_privacy", "zanzibar_2019", 2019, "Zanzibar: Google's Consistent, Global Authorization System", "https://research.google/pubs/zanzibar-googles-consistent-global-authorization-system/", "USENIX ATC", ["Ruoming Pang", "Ramon Caceres", "Mike Burrows", "Zhifeng Chen", "Pratik Dave", "Nathan Germer", "Alexander Golynski", "Kevin Graney", "Nina Kang", "Lea Kissner", "Jeffrey L. Korn", "Abhishek Parmar", "Christopher D. Richards", "Mengzhi Wang"]),
    A("security_privacy", "privacy_loss_distribution_2021", 2021, "Computing Tight Differential Privacy Guarantees Using FFT", "https://proceedings.mlr.press/v130/koskela21a.html", "AISTATS", ["Antti Koskela", "Joonas Jälkö", "Antti Honkela"]),
    A("security_privacy", "slsa_2023", 2023, "Supply-chain Levels for Software Artifacts Specification v1.0", "https://slsa.dev/spec/v1.0/", "SLSA specification", ["SLSA community contributors"], kind="standard"),

    # Data quality, governance, lineage, and provenance.
    A("quality_governance_provenance", "data_quality_1996", 1996, "Beyond Accuracy: What Data Quality Means to Data Consumers", "https://doi.org/10.1080/07421222.1996.11518099", "Journal of Management Information Systems", ["Richard Y. Wang", "Diane M. Strong"], deep=True),
    A("quality_governance_provenance", "why_provenance_2001", 2001, "Why and Where: A Characterization of Data Provenance", "https://doi.org/10.1007/3-540-44503-X_20", "ICDT", ["Peter Buneman", "Sanjeev Khanna", "Wang-Chiew Tan"]),
    A("quality_governance_provenance", "semiring_provenance_2007", 2007, "Provenance Semirings", "https://doi.org/10.1145/1265530.1265535", "PODS", ["Todd J. Green", "Grigoris Karvounarakis", "Val Tannen"], deep=True),
    A("quality_governance_provenance", "w3c_prov_2013", 2013, "PROV-DM: The PROV Data Model", "https://www.w3.org/TR/prov-dm/", "W3C Recommendation", ["Luc Moreau", "Paolo Missier", "W3C Provenance Working Group"], kind="standard"),
    A("quality_governance_provenance", "fair_2016", 2016, "The FAIR Guiding Principles for Scientific Data Management and Stewardship", "https://doi.org/10.1038/sdata.2016.18", "Scientific Data", ["Mark D. Wilkinson", "Michel Dumontier", "IJsbrand Jan Aalbersberg", "Gabrielle Appleton", "Myles Axton", "Arie Baak", "Niklas Blomberg", "Jan-Willem Boiten", "Luiz Bonino da Silva Santos", "Philip E. Bourne", "Jildau Bouwman", "Anthony J. Brookes", "Tim Clark", "Mercè Crosas", "Ingrid Dillo", "Olivier Dumon", "Scott Edmunds", "Chris T. Evelo", "Richard Finkers", "Alejandra Gonzalez-Beltran", "Alasdair J. G. Gray", "Paul Groth", "Carole Goble", "Jeffrey S. Grethe", "Jaap Heringa", "Peter A. C. 't Hoen", "Rob Hooft", "Tobias Kuhn", "Ruben Kok", "Joost Kok", "Scott J. Lusher", "Maryann E. Martone", "Albert Mons", "Abel L. Packer", "Bengt Persson", "Philippe Rocca-Serra", "Marco Roos", "Rene van Schaik", "Susanna-Assunta Sansone", "Erik Schultes", "Thierry Sengstag", "Ted Slater", "George Strawn", "Morris A. Swertz", "Mark Thompson", "Johan van der Lei", "Erik van Mulligen", "Jan Velterop", "Andra Waagmeester", "Peter Wittenburg", "Katherine Wolstencroft", "Jun Zhao", "Barend Mons"]),
    A("quality_governance_provenance", "shacl_2017", 2017, "Shapes Constraint Language (SHACL)", "https://www.w3.org/TR/shacl/", "W3C Recommendation", ["Holger Knublauch", "Dimitris Kontokostas"], kind="standard"),
    A("quality_governance_provenance", "deequ_2018", 2018, "Automating Large-Scale Data Quality Verification", "https://doi.org/10.14778/3229863.3229867", "PVLDB", ["Sebastian Schelter", "Dustin Lange", "Philipp Schmidt", "Melanie Celikel", "Felix Biessmann", "Andrey Grafberger"]),
    A("quality_governance_provenance", "datasheets_2021", 2021, "Datasheets for Datasets", "https://doi.org/10.1145/3458723", "Communications of the ACM", ["Timnit Gebru", "Jamie Morgenstern", "Briana Vecchione", "Jennifer Wortman Vaughan", "Hanna Wallach", "Hal Daumé III", "Kate Crawford"]),
    A("quality_governance_provenance", "openlineage_2021", 2021, "OpenLineage Specification", "https://openlineage.io/docs/spec/object-model/", "OpenLineage specification", ["OpenLineage contributors"], kind="standard", deep=True),
    A("quality_governance_provenance", "data_cards_2022", 2022, "Data Cards: Purposeful and Transparent Dataset Documentation for Responsible AI", "https://doi.org/10.1145/3531146.3533231", "FAccT", ["Mahima Pushkarna", "Andrew Zaldivar", "Oddur Kjartansson"]),
]


DEEP = {
    "artifact.codd_relational_1970": {
        "question": "How can shared data be represented independently of physical access paths?",
        "definitions": ["relation", "primary key", "foreign key", "normal form"],
        "assumptions": ["data is described through n-ary relations"],
        "claims": ["logical data independence follows from separating relation semantics from physical representation"],
        "methods": ["relational data modeling"], "algorithms": [],
        "practice": ["logical_schema_design"], "operations": ["relational_query"],
        "representations": ["relation"], "kernels": [], "libraries": ["relational_algebra_types"],
        "limitations": ["does not itself select a physical execution plan"],
    },
    "artifact.selinger_access_paths_1979": {
        "question": "How can a relational optimizer choose join orders and access paths?",
        "definitions": ["access path", "interesting order", "cost estimate"],
        "assumptions": ["cost/cardinality models approximate a target DBMS and workload"],
        "claims": ["dynamic programming can search useful join orders while retaining interesting orders"],
        "methods": ["cost-based query optimization"], "algorithms": ["Selinger join enumeration"],
        "practice": ["query_optimization"], "operations": ["plan_enumeration"],
        "representations": ["logical_plan", "physical_plan"], "kernels": [], "libraries": ["optimizer_search"],
        "limitations": ["quality depends on statistics, cost assumptions, and search-space restrictions"],
    },
    "artifact.dataflow_2015": {
        "question": "How should unbounded out-of-order computation express event time and output refinement?",
        "definitions": ["event time", "processing time", "window", "trigger", "watermark", "accumulation mode"],
        "assumptions": ["records have event-time semantics and execution observes incomplete prefixes"],
        "claims": ["what/where/when/how decomposition exposes correctness-latency-cost decisions"],
        "methods": ["event-time stream processing"], "algorithms": ["watermark and trigger execution"],
        "practice": ["stream_processing"], "operations": ["window", "trigger", "late_data_revision"],
        "representations": ["unbounded_collection"], "kernels": ["window_aggregation"], "libraries": ["temporal_dataflow"],
        "limitations": ["watermarks are progress estimates, not proof that no earlier event can arrive"],
    },
    "artifact.mlir_2021": {
        "question": "How can compiler infrastructure represent and progressively lower domain-specific operations?",
        "definitions": ["dialect", "operation", "region", "type", "attribute", "rewrite", "conversion"],
        "assumptions": ["dialects define explicit verification and conversion contracts"],
        "claims": ["multi-level reusable IRs reduce forced early lowering and preserve domain information"],
        "methods": ["multi-level intermediate representation"], "algorithms": ["dialect conversion"],
        "practice": ["compiler_architecture"], "operations": ["verify_ir", "lower_ir"],
        "representations": ["dialect_ir"], "kernels": [], "libraries": ["ir_core", "dialect_registry", "rewrite_engine"],
        "limitations": ["an IR framework does not supply a domain ontology or prove a lowering is semantically correct"],
    },
    "artifact.hnsw_2016": {
        "question": "How can approximate nearest-neighbor search navigate large metric datasets efficiently?",
        "definitions": ["proximity graph", "hierarchical layers", "efSearch", "efConstruction"],
        "assumptions": ["distance function and dataset geometry support useful graph navigation"],
        "claims": ["hierarchical navigable small-world graphs offer an effective recall-latency tradeoff"],
        "methods": ["approximate nearest-neighbor search"], "algorithms": ["HNSW construction", "HNSW search"],
        "practice": ["similarity_search"], "operations": ["build_ann_index", "query_ann_index"],
        "representations": ["proximity_graph", "vector"], "kernels": ["distance_kernel", "graph_traversal"], "libraries": ["ann_index"],
        "limitations": ["no universal recall/latency guarantee across distance, distribution, parameters, hardware, or mutations"],
    },
    "artifact.vega_lite_2017": {
        "question": "How can interactive visualizations be specified declaratively?",
        "definitions": ["mark", "encoding", "transform", "selection", "composition"],
        "assumptions": ["data fields and semantic types are declared correctly"],
        "claims": ["a concise grammar can compile into lower-level Vega specifications"],
        "methods": ["grammar-based visualization"], "algorithms": ["visualization specification compilation"],
        "practice": ["visual_analytics"], "operations": ["encode_visualization", "compile_visualization"],
        "representations": ["declarative_visual_spec"], "kernels": ["scale_mapping", "layout"], "libraries": ["visual_grammar"],
        "limitations": ["syntactic validity does not establish perceptual fitness, accessibility, or truthful semantics"],
    },
    "artifact.xgboost_2016": {
        "question": "How can gradient-boosted trees be trained efficiently at scale?",
        "definitions": ["additive tree model", "regularized objective", "sparsity-aware split finding", "weighted quantile sketch"],
        "assumptions": ["supervised labels and features are available; deployment distribution is not arbitrarily shifted"],
        "claims": ["system and algorithmic optimizations enable scalable gradient-tree boosting"],
        "methods": ["gradient boosting"], "algorithms": ["XGBoost training", "tree ensemble inference"],
        "practice": ["predictive_modeling"], "operations": ["fit_model", "predict"],
        "representations": ["feature_matrix", "tree_ensemble"], "kernels": ["histogram_build", "split_evaluation"], "libraries": ["boosted_tree_model"],
        "limitations": ["benchmarks do not establish calibration, causal validity, fairness, or robustness for a new domain"],
    },
    "artifact.double_ml_2018": {
        "question": "How can nuisance machine learning be combined with inference on causal/structural parameters?",
        "definitions": ["target parameter", "nuisance function", "orthogonal score", "cross-fitting"],
        "assumptions": ["identification, overlap, suitable rates, sampling, and score conditions hold"],
        "claims": ["orthogonalization and cross-fitting can reduce regularization bias in target-parameter inference"],
        "methods": ["double machine learning", "causal estimation"], "algorithms": ["cross-fitted orthogonal estimation"],
        "practice": ["causal_analytics"], "operations": ["define_estimand", "fit_nuisance", "estimate_effect"],
        "representations": ["study_design", "estimand", "estimator"], "kernels": ["cross_fit"], "libraries": ["causal_estimation"],
        "limitations": ["prediction accuracy alone does not identify a causal effect; assumptions remain domain obligations"],
    },
    "artifact.conformal_prediction_2005": {
        "question": "How can predictive uncertainty sets obtain finite-sample coverage under explicit exchangeability assumptions?",
        "definitions": ["nonconformity score", "prediction set", "coverage", "exchangeability"],
        "assumptions": ["exchangeability or the selected conformal variant's explicit replacement assumption"],
        "claims": ["conformal procedures provide marginal coverage guarantees under their assumptions"],
        "methods": ["conformal prediction"], "algorithms": ["split conformal prediction"],
        "practice": ["predictive_uncertainty"], "operations": ["calibrate_prediction_set", "predict_set"],
        "representations": ["calibration_set", "prediction_interval"], "kernels": ["quantile_selection"], "libraries": ["uncertainty_quantification"],
        "limitations": ["marginal coverage is not conditional coverage and can fail under distribution shift"],
    },
    "artifact.ekg_dimensions_2022": {
        "question": "How can process behavior over multiple entities be represented without forcing a single case identifier?",
        "definitions": ["event knowledge graph", "entity", "event", "correlation", "entity-relative directly-follows"],
        "assumptions": ["source-to-event/entity semantics are explicitly constructed"],
        "claims": ["event knowledge graphs enable multiple behavioral dimensions and graph-based aggregation"],
        "methods": ["event knowledge graph process mining"], "algorithms": ["entity-relative directly-follows construction"],
        "practice": ["multidimensional_process_analytics"], "operations": ["construct_event_graph", "query_event_graph", "aggregate_event_graph"],
        "representations": ["labeled_property_graph"], "kernels": ["graph_pattern_match", "graph_aggregation"], "libraries": ["event_knowledge_graph"],
        "limitations": ["the graph does not remove the need to define event/entity identity, time, relation semantics, and aggregation validity"],
    },
    "artifact.ocel2_2023": {
        "question": "How can object-centric event logs exchange events, objects, qualified relations, and changing object attributes?",
        "definitions": ["event type", "event", "object type", "object", "E2O relation", "O2O relation", "qualifier", "object attribute change"],
        "assumptions": ["producer-defined identifiers, types, qualifiers, and timestamps have stable intended meanings"],
        "claims": ["OCEL 2.0 defines interoperable JSON, XML, and relational representations for its metamodel"],
        "methods": ["object-centric event data interchange"], "algorithms": [],
        "practice": ["object_centric_event_data"], "operations": ["parse_ocel", "validate_ocel", "serialize_ocel"],
        "representations": ["OCEL_2_met_model", "OCEL_JSON", "OCEL_XML", "OCEL_SQLite"], "kernels": ["temporal_attribute_lookup"], "libraries": ["ocel_core", "ocel_codec"],
        "limitations": ["exchange conformance does not prove source semantics, case fitness, process correctness, or lossless transformation from arbitrary systems"],
    },
    "artifact.oced_pg_2024": {
        "question": "How can legacy data plus domain knowledge be declaratively transformed into OCED-compliant event knowledge graphs?",
        "definitions": ["semantic header", "OCED-PG", "PG-Schema", "domain ontology"],
        "assumptions": ["a domain expert supplies correct mapping semantics in the header"],
        "claims": ["a semantic header can be translated into database queries constructing an OCED/domain-ontology-compliant graph"],
        "methods": ["declarative event-data extraction"], "algorithms": ["semantic-header query generation"],
        "practice": ["event_data_preparation"], "operations": ["compile_semantic_header", "construct_oced_pg"],
        "representations": ["semantic_header", "PG_Schema", "event_knowledge_graph"], "kernels": ["graph_load_transform"], "libraries": ["semantic_header_types", "oced_pg_builder"],
        "limitations": ["seven demonstrations do not establish universal source coverage; mapping truth remains externally supplied"],
    },
    "artifact.oced_core_2024": {
        "question": "What minimal core and explicit design space should a general OCED standard expose?",
        "definitions": ["OCED core model", "event", "object", "event-object relation", "object-object relation", "design choice"],
        "assumptions": ["extensions preserve core identity and relationship laws"],
        "claims": ["a small extensible core plus explicit design choices can reduce accidental incompatibility"],
        "methods": ["event-data metamodel design"], "algorithms": [],
        "practice": ["event_data_standardization"], "operations": ["extend_oced_core", "validate_oced_profile"],
        "representations": ["OCED_core", "OCED_profile"], "kernels": [], "libraries": ["oced_core_types", "oced_extension_registry"],
        "limitations": ["preprint/proposal maturity; profile compatibility and exchange bindings require separate proof"],
    },
    "artifact.tekg_2024": {
        "question": "How can OCEL 2.0 time-varying object information be transformed into a temporal event knowledge graph?",
        "definitions": ["temporal event knowledge graph", "entity snapshot", "temporal relation", "derived directly-follows"],
        "assumptions": ["OCEL temporal values and relation semantics are valid and transformation ordering is defined"],
        "claims": ["an explicit transformation can materialize temporal snapshots and relations from OCEL 2.0"],
        "methods": ["temporal event graph transformation"], "algorithms": ["OCEL-to-tEKG transformation", "directly-follows reduction"],
        "practice": ["temporal_process_analytics"], "operations": ["snapshot_entity_state", "transform_ocel_to_tekg"],
        "representations": ["OCEL_2", "temporal_event_knowledge_graph"], "kernels": ["temporal_snapshot_materialization", "graph_edge_reduction"], "libraries": ["tekg_types", "ocel_tekg_transform"],
        "limitations": ["the tEKG paper cites Fahland's EKG foundation but its listed authors are Khayatbashi, Hartig, and Jalali"],
    },
    "artifact.sa_ocpm_2026": {
        "question": "How can operational object states and transitions become explicit in object-centric process analysis?",
        "definitions": ["state model", "state function", "object state transition event", "object state-aware event"],
        "assumptions": ["a domain-specific state function over time is supplied or learned and its validity is assessed"],
        "claims": ["explicit transition events and state-aware labels enable analysis conditioned on object state"],
        "methods": ["state-aware object-centric process mining"], "algorithms": ["state transition event enrichment", "state-aware relabeling"],
        "practice": ["state_conditioned_process_diagnostics"], "operations": ["derive_object_state", "emit_state_transition", "label_event_by_state"],
        "representations": ["state_model", "state_enriched_OCEL"], "kernels": ["temporal_state_lookup"], "libraries": ["state_model_contract", "sa_ocpm_enrichment"],
        "limitations": ["state semantics are domain decisions; thresholds or learned states are not universally interchangeable"],
    },
    "artifact.predictive_ocpm_2022": {
        "question": "Can object attributes improve remaining-event and timestamp prediction for object-centric process monitoring?",
        "definitions": ["ongoing object-centric execution", "remaining-event sequence", "timestamp prediction"],
        "assumptions": ["training/evaluation log construction, feature selection, and split protocol match intended deployment"],
        "claims": ["reported performance matches or exceeds baselines depending on whether selected object attributes are useful"],
        "methods": ["predictive object-centric process monitoring"], "algorithms": ["GAN/LSTM/seq2seq prediction pipeline"],
        "practice": ["predictive_process_monitoring"], "operations": ["construct_predictive_prefix", "fit_sequence_model", "predict_remaining_sequence"],
        "representations": ["OCEL", "execution_prefix", "prediction"], "kernels": ["sequence_model_training", "sequence_decoding"], "libraries": ["predictive_monitoring_pipeline"],
        "limitations": ["thesis evidence; conditional result; model family is not a universal predictive default"],
    },
    "artifact.differential_privacy_2006": {
        "question": "How can query output distributions limit disclosure from one individual's participation?",
        "definitions": ["adjacent datasets", "sensitivity", "epsilon-differential privacy", "noise mechanism"],
        "assumptions": ["adjacency, query sensitivity, and composition scope are defined correctly"],
        "claims": ["calibrated noise can provide a formal indistinguishability guarantee"],
        "methods": ["differential privacy"], "algorithms": ["Laplace mechanism"],
        "practice": ["privacy_preserving_analytics"], "operations": ["bound_sensitivity", "allocate_privacy_budget", "release_noisy_result"],
        "representations": ["privacy_accountant", "mechanism_contract"], "kernels": ["noise_sampling"], "libraries": ["privacy_mechanisms", "privacy_accounting"],
        "limitations": ["privacy guarantee depends on adjacency, budget accounting, mechanism implementation, and side-channel boundaries"],
    },
    "artifact.semiring_provenance_2007": {
        "question": "How can positive relational queries propagate general provenance annotations compositionally?",
        "definitions": ["provenance semiring", "annotation", "positive relational algebra"],
        "assumptions": ["query fragment and annotation algebra satisfy stated semiring laws"],
        "claims": ["semiring annotations provide a uniform compositional account of multiple provenance interpretations"],
        "methods": ["algebraic data provenance"], "algorithms": ["semiring annotation propagation"],
        "practice": ["lineage_provenance"], "operations": ["propagate_provenance"],
        "representations": ["K_relation", "provenance_polynomial"], "kernels": ["annotation_add", "annotation_multiply"], "libraries": ["provenance_algebra"],
        "limitations": ["scope is tied to query fragment and chosen algebra; operational lineage collection is a separate concern"],
    },
    "artifact.osqp_2020": {
        "question": "How can convex quadratic programs be solved robustly with operator splitting?",
        "definitions": ["quadratic program", "primal residual", "dual residual", "infeasibility certificate"],
        "assumptions": ["problem matches supported convex quadratic form and numerical tolerances are explicit"],
        "claims": ["an ADMM-based solver can exploit quasi-definite linear systems and warm starts"],
        "methods": ["convex optimization"], "algorithms": ["OSQP operator splitting"],
        "practice": ["prescriptive_analytics"], "operations": ["canonicalize_qp", "solve_qp", "check_certificate"],
        "representations": ["quadratic_program", "solver_status"], "kernels": ["sparse_linear_solve"], "libraries": ["qp_solver_adapter"],
        "limitations": ["solver status/tolerance/conditioning must remain visible; feasible or optimal is never inferred from a numeric vector alone"],
    },
}


RELATION_TYPES = [
    ("edition_of_work", "edition", "work", "Edition identity remains distinct from the abstract scholarly work."),
    ("venue_occurrence_hosts_edition", "venue_occurrence", "edition", "Venue occurrence is dated and does not become the work identity."),
    ("artifact_manifests_edition", "artifact", "edition", "Exact downloadable/identified artifact manifests one edition."),
    ("artifact_authored_by", "artifact", "person", "Bibliographic contribution only; never implies sole invention."),
    ("artifact_affiliated_with", "person", "institution", "Affiliation at the artifact occurrence, not permanent identity."),
    ("artifact_defines", "artifact", "concept", "Artifact supplies an explicit definition in a cited edition."),
    ("artifact_introduces_method", "artifact", "method", "Requires textual evidence; first-publication priority remains unadjudicated."),
    ("artifact_describes_algorithm", "artifact", "algorithm", "Pseudocode/steps, distinct from implementation."),
    ("algorithm_implements_method", "algorithm", "method", "Algorithm realizes some method under assumptions."),
    ("implementation_realizes_algorithm", "implementation", "algorithm", "Exact version/commit required for binding."),
    ("artifact_evaluates_on", "artifact", "benchmark", "Evaluation protocol and partition must be retained."),
    ("claim_supported_by", "claim", "evidence", "Support is scoped, defeasible, and never global by default."),
    ("claim_contradicts", "claim", "claim", "Only after question, estimand, population, protocol, and metric alignment."),
    ("artifact_extends", "artifact", "artifact", "Adds semantics/operations; does not erase predecessor identity."),
    ("artifact_transforms_to", "artifact", "artifact", "A documented representational transformation, not equivalence."),
    ("artifact_supersedes_edition", "artifact", "artifact", "Edition relation; earlier historical evidence remains addressable."),
    ("artifact_replicated_by", "artifact", "artifact", "Replication kind and deviations must be explicit."),
    ("artifact_maps_to_compiler", "artifact", "compiler_mapping", "Research-derived candidate mapping, gated by adjudication."),
]


CONVERSION_RULES = [
    ("publication_not_concept", "Publication identity MUST NOT be used as concept identity; multiple artifacts may define or contest one concept."),
    ("claim_not_law", "A paper claim MUST remain scoped evidence until assumptions, protocol, population, metric, and uncertainty are adjudicated."),
    ("method_algorithm_implementation_split", "Method, algorithm, implementation, and deployed occurrence MUST have independent identifiers and compatibility proofs."),
    ("benchmark_not_qualification", "A benchmark result MUST NOT satisfy a target qualification without matching dataset, scale, hardware, software edition, configuration, metric, and protocol."),
    ("definition_to_type", "A definition MAY create a semantic type candidate only with equality, validity, construction, canonicalization, and loss rules."),
    ("theorem_to_proof_obligation", "A theorem MAY become a compiler proof obligation only within its formal assumptions and guarantee scope."),
    ("pseudocode_to_algorithm_ir", "Pseudocode MAY lower to algorithm IR only after totality, partiality, complexity, numerical, concurrency, and determinism decisions are explicit."),
    ("implementation_to_library", "Code MAY become a library contribution only with license/IP, version, public API, failure model, unsafe/FFI, resource envelope, and conformance evidence."),
    ("dataset_to_test_fixture", "A research dataset MAY become a test fixture only when license, schema/semantics, privacy, split, checksum, and transformation provenance are known."),
    ("negative_result_to_refusal", "A limitation or failed assumption SHOULD compile into a refusal, diagnostic, qualification exclusion, or review requirement."),
    ("predictive_model_contract", "A predictive model requires task, target, horizon, population, features available-at-decision-time, loss, calibration, uncertainty, drift, and retraining contracts."),
    ("causal_model_contract", "A causal method requires estimand, identification assumptions, design, nuisance estimation, diagnostics, sensitivity, and transport scope; prediction is insufficient."),
    ("process_state_contract", "A process state requires an owning domain, state function, valid-time policy, transition law, ambiguity/refusal behavior, and provenance."),
    ("event_transform_contract", "Event-data transformations require identity, ordering, time, multiplicity, qualifier, attribute-validity, and information-loss receipts."),
    ("standard_profile_contract", "A standard name is insufficient: exact edition/profile/serialization plus extension and compatibility rules are required."),
    ("author_not_inventor", "Authorship, citation count, affiliation, or popularity MUST NOT be converted into invention priority or exclusive expertise."),
]


def generate():
    ROOT.mkdir(parents=True, exist_ok=True)
    (ROOT / "schemas").mkdir(exist_ok=True)

    artifacts, works, editions, venue_occurrences = [], [], [], []
    people, contributions, sources, evidence = {}, [], [], []
    concepts, claims, methods, algorithms, implementations, benchmarks = [], [], [], [], [], []
    relations, mappings, reviews = [], [], []

    for seed in ARTIFACTS:
        effective_deep = seed["id"] in DEEP
        work_id = "work." + seed["key"]
        edition_id = "edition." + seed["key"] + "." + slug(seed["version"])
        occurrence_id = "venue_occurrence." + seed["key"] + "." + str(seed["year"])
        works.append({
            "id": work_id, "record_type": "work", "canonical_title_candidate": seed["title"],
            "category": seed["category"], "identity_status": "candidate",
            "priority_claim": "not_adjudicated",
        })
        editions.append({
            "id": edition_id, "record_type": "edition", "work_id": work_id,
            "edition_label": seed["version"], "year": seed["year"],
            "version_status": "exact_where_standard_else_version_of_record_candidate",
        })
        venue_occurrences.append({
            "id": occurrence_id, "record_type": "venue_occurrence", "venue": seed["venue"],
            "year": seed["year"], "edition_id": edition_id,
            "occurrence_identity_status": "candidate_from_primary_metadata",
        })
        item = {k: v for k, v in seed.items() if k not in {"authors", "key", "deep"}}
        item.update({
            "record_type": "artifact", "current_as_of": AS_OF, "non_llm": True,
            "work_id": work_id, "edition_id": edition_id, "venue_occurrence_id": occurrence_id,
            "identity_basis": "title+year+primary_url+edition",
            "extraction_status": "deep" if effective_deep else "metadata_only",
            "evidence_scope": "bibliographic_and_abstract" if effective_deep else "bibliographic_only",
            "license_ip_status": "review_required",
            "implementation_maturity": "not_applicable_or_unassessed",
            "do_not_infer": ["priority_of_invention", "universal_validity", "production_readiness"],
        })
        artifacts.append(item)
        src_id = "source." + seed["key"]
        sources.append({
            "id": src_id, "record_type": "source", "source_kind": "primary_research_or_standard",
            "url": seed["primary_url"], "title": seed["title"], "publisher_or_venue": seed["venue"],
            "artifact_id": seed["id"], "edition": seed["version"], "checked_on": AS_OF,
            "supports": ["identity", "year", "title", "venue", "deep_fields" if effective_deep else "coverage_presence"],
            "limitations": ["metadata-only entries require full-text adjudication"] if not effective_deep else ["claim scope remains limited to cited artifact"],
        })
        ev_id = "evidence." + seed["key"]
        evidence.append({
            "id": ev_id, "record_type": "evidence", "source_id": src_id, "artifact_id": seed["id"],
            "evidence_kind": "primary_artifact", "scope": item["evidence_scope"],
            "supports_fields": sources[-1]["supports"], "confidence": "candidate" if not effective_deep else "high_for_extracted_scope",
            "excludes": ["cross-domain effectiveness", "invention priority", "deployment qualification"],
        })
        relations.extend([
            {"id": "relation.edition_work." + seed["key"], "record_type": "relation", "relation_type": "edition_of_work", "from_id": edition_id, "to_id": work_id, "evidence_id": ev_id, "adjudication": "candidate"},
            {"id": "relation.venue_edition." + seed["key"], "record_type": "relation", "relation_type": "venue_occurrence_hosts_edition", "from_id": occurrence_id, "to_id": edition_id, "evidence_id": ev_id, "adjudication": "candidate"},
            {"id": "relation.artifact_edition." + seed["key"], "record_type": "relation", "relation_type": "artifact_manifests_edition", "from_id": seed["id"], "to_id": edition_id, "evidence_id": ev_id, "adjudication": "candidate"},
        ])
        for order, name in enumerate(seed["authors"], 1):
            pid = stable_id("person", name)
            if pid not in people:
                people[pid] = {
                    "id": pid, "record_type": "person", "display_name": name,
                    "identity_status": "candidate_name_identity",
                    "external_ids": [], "do_not_merge_on_name_only": True,
                }
            contributions.append({
                "id": stable_id("contribution", seed["id"] + "|" + name), "record_type": "contribution",
                "artifact_id": seed["id"], "person_id": pid, "role": "credited_author_or_collective_contributor",
                "ordinal": order, "role_source_id": src_id, "contribution_scope": "bibliographic_credit_only",
                "does_not_establish": ["invention_priority", "specific_section_authorship", "implementation_authorship"],
            })
        if not effective_deep:
            reviews.append({
                "id": "review.deep_extract." + seed["key"], "record_type": "review_item", "priority": "normal",
                "artifact_id": seed["id"], "reason": "metadata_only_candidate",
                "required": ["verify_complete_contributor_list", "extract_problem_definitions_assumptions_claims_algorithms_protocol_results_limitations_artifacts_license", "adjudicate_mappings"],
                "promotion_gate": "two_person_or_primary_full_text_review",
            })

    # Institutions are intentionally explicit and occurrence-scoped. We do not infer all
    # historical affiliations for every author from a current profile.
    institutions = [
        {"id": "institution.tue", "record_type": "institution", "name": "Eindhoven University of Technology", "identity_status": "verified_primary_profile", "source": "https://research.tue.nl/"},
        {"id": "institution.rwth_pads", "record_type": "institution", "name": "RWTH Aachen Process and Data Science", "identity_status": "verified_primary_standard", "source": "https://www.ocel-standard.org/2.0/ocel20_specification.pdf"},
        {"id": "institution.oced_working_group", "record_type": "institution", "name": "IEEE Task Force on Process Mining OCED working group", "identity_status": "candidate_collective", "source": "https://arxiv.org/abs/2410.14495"},
    ]

    for aid, detail in DEEP.items():
        key = aid.removeprefix("artifact.")
        for definition in detail["definitions"]:
            cid = stable_id("concept", definition)
            if not any(x["id"] == cid for x in concepts):
                concepts.append({
                    "id": cid, "record_type": "concept", "label": definition,
                    "status": "artifact_scoped_definition_candidate", "equality": "not_yet_adjudicated",
                    "scope_artifact_ids": [aid], "do_not_merge_by_label": True,
                })
            else:
                next(x for x in concepts if x["id"] == cid)["scope_artifact_ids"].append(aid)
            relations.append({"id": stable_id("relation", aid + "|defines|" + cid), "record_type": "relation", "relation_type": "artifact_defines", "from_id": aid, "to_id": cid, "evidence_id": "evidence." + key, "adjudication": "candidate"})
        for i, claim_text in enumerate(detail["claims"], 1):
            claim_id = f"claim.{key}.{i}"
            claims.append({
                "id": claim_id, "record_type": "claim", "artifact_id": aid, "text": claim_text,
                "claim_kind": "artifact_claim", "assumptions": detail["assumptions"],
                "population_or_scope": detail["question"], "uncertainty": "as_reported_in_artifact_not_yet_normalized",
                "status": "scoped_candidate", "evidence_ids": ["evidence." + key],
                "limitations": detail["limitations"],
            })
        for name in detail["methods"]:
            mid = stable_id("method", name)
            if not any(x["id"] == mid for x in methods):
                methods.append({"id": mid, "record_type": "method", "label": name, "purpose": detail["question"], "assumption_contract": detail["assumptions"], "status": "candidate"})
            relations.append({"id": stable_id("relation", aid + "|method|" + mid), "record_type": "relation", "relation_type": "artifact_introduces_method", "from_id": aid, "to_id": mid, "evidence_id": "evidence." + key, "adjudication": "describes_or_uses; priority_not_claimed"})
        for name in detail["algorithms"]:
            alg_id = stable_id("algorithm", name)
            if not any(x["id"] == alg_id for x in algorithms):
                algorithms.append({
                    "id": alg_id, "record_type": "algorithm", "label": name,
                    "pseudocode_status": "extract_from_primary_artifact", "complexity": "extract_or_derive_with_proof",
                    "guarantee": "scoped_to_artifact_assumptions", "totality": "not_yet_adjudicated",
                    "determinism": "not_yet_adjudicated", "numerical_contract": "not_yet_adjudicated",
                })
            relations.append({"id": stable_id("relation", aid + "|algorithm|" + alg_id), "record_type": "relation", "relation_type": "artifact_describes_algorithm", "from_id": aid, "to_id": alg_id, "evidence_id": "evidence." + key, "adjudication": "candidate"})
        mappings.append({
            "id": "mapping." + key, "record_type": "compiler_mapping", "artifact_id": aid,
            "problem_question": detail["question"], "practice_refs": detail["practice"],
            "operation_refs": detail["operations"], "representation_refs": detail["representations"],
            "kernel_refs": detail["kernels"], "library_candidates": detail["libraries"],
            "product_capability_candidates": [p + "_capability" for p in detail["practice"]],
            "product_boundary_status": "requires_separate_demand_operability_and_economics_evidence",
            "compiler_phases": ["semantic_resolution", "requirement_elaboration", "algorithm_selection", "target_qualification", "proof_receipt_emission"],
            "proof_obligations": ["assumption_satisfaction", "information_loss", "algorithm_applicability", "implementation_qualification", "evidence_scope"],
            "binding_status": "research_candidate_not_bindable",
        })

    # Concrete implementation and benchmark identities used to demonstrate non-collapsing edges.
    implementations.extend([
        {"id": "implementation.promg", "record_type": "implementation", "name": "PromG", "version": "v0.1.25_occurrence", "url": "https://github.com/promg-dev", "license": "verify_exact_repository_and_revision", "maturity": "research_implementation", "artifact_ids": ["artifact.oced_pg_2024"]},
        {"id": "implementation.pm4py_ocel", "record_type": "implementation", "name": "PM4Py OCEL support", "version": "unbound", "url": "https://github.com/process-intelligence-solutions/pm4py", "license": "GPL-3.0_candidate_verify", "maturity": "open_source_library", "artifact_ids": ["artifact.ocel2_2023"]},
        {"id": "implementation.xgboost", "record_type": "implementation", "name": "XGBoost", "version": "unbound", "url": "https://github.com/dmlc/xgboost", "license": "Apache-2.0_candidate_verify", "maturity": "production_library", "artifact_ids": ["artifact.xgboost_2016"]},
        {"id": "implementation.osqp", "record_type": "implementation", "name": "OSQP", "version": "unbound", "url": "https://github.com/osqp/osqp", "license": "Apache-2.0_candidate_verify", "maturity": "production_library", "artifact_ids": ["artifact.osqp_2020"]},
    ])
    benchmarks.extend([
        {"id": "benchmark.bpic_family", "record_type": "benchmark", "name": "BPI Challenge event-log family", "dataset_identity": "multiple_editioned_datasets", "protocol": "artifact_specific", "metric_contract": "artifact_specific", "license": "per_dataset", "reusability": "requires_exact_dataset_and_split"},
        {"id": "benchmark.ann_benchmarks", "record_type": "benchmark", "name": "ANN-Benchmarks", "dataset_identity": "suite_and_commit_required", "protocol": "recall_vs_query_performance", "metric_contract": "implementation_and_hardware_scoped", "license": "verify_exact_revision", "reusability": "qualification_seed_only"},
        {"id": "benchmark.tpc_h", "record_type": "benchmark", "name": "TPC-H", "dataset_identity": "scale_factor_and_kit_edition_required", "protocol": "TPC_rules_required", "metric_contract": "not_equivalent_to_arbitrary_analytics_workload", "license": "TPC_terms", "reusability": "research_comparison_only_until_qualified"},
    ])

    conflict_replication = [
        {"id": "case.ocel_oced_tekg", "record_type": "conflict_replication_case", "kind": "related_models_not_synonyms", "artifact_ids": ["artifact.ocel2_2023", "artifact.oced_core_2024", "artifact.oced_pg_2024", "artifact.tekg_2024"], "finding": "OCEL 2.0 exchange, an OCED core/profile, OCED-PG construction, and tEKG transformation have different identities and proof obligations.", "compiler_action": "require_explicit_profile_and_loss_receipt", "status": "adjudicated_example"},
        {"id": "case.fahland_attribution", "record_type": "conflict_replication_case", "kind": "attribution_boundary", "artifact_ids": ["artifact.ekg_dimensions_2022", "artifact.oced_pg_2024", "artifact.oced_core_2024", "artifact.tekg_2024", "artifact.sa_ocpm_2026"], "finding": "Fahland authored the EKG chapter and coauthored OCED-PG/core work; the listed tEKG and SA-OCPM artifacts have different author lists. Citation lineage is not authorship.", "compiler_action": "preserve_contribution_edges_and_citation_lineage", "status": "primary_metadata_verified"},
        {"id": "case.predictive_ocpm_scope", "record_type": "conflict_replication_case", "kind": "conditional_result", "artifact_ids": ["artifact.predictive_ocpm_2022"], "finding": "Reported gains depend on usefulness of selected object attributes and a thesis evaluation protocol.", "compiler_action": "require_target_specific_requalification", "status": "adjudicated_example"},
        {"id": "case.ann_benchmark_non_portability", "record_type": "conflict_replication_case", "kind": "benchmark_non_portability", "artifact_ids": ["artifact.hnsw_2016", "artifact.ann_benchmarks_2021", "artifact.spann_2021"], "finding": "Recall/latency rankings can change with data distribution, metric, parameters, hardware, implementation, build budget, and update regime.", "compiler_action": "emit_qualification_plan_not_static_winner", "status": "adjudicated_example"},
        {"id": "case.compression_benchmark_non_equivalence", "record_type": "conflict_replication_case", "kind": "benchmark_non_portability", "artifact_ids": ["artifact.fsst_2020", "artifact.btrblocks_2023", "artifact.leco_2024", "artifact.alp_2023"], "finding": "String, block, integer/correlated-value, and floating-point codec results answer different carrier/workload questions.", "compiler_action": "select_codec_after_type_layout_workload_target_qualification", "status": "adjudicated_example"},
        {"id": "case.mlir_not_domain_model", "record_type": "conflict_replication_case", "kind": "architecture_boundary", "artifact_ids": ["artifact.mlir_2021"], "finding": "Multi-level IR infrastructure can host domain dialects but does not discover vocabulary, bounded contexts, or semantic laws.", "compiler_action": "keep_domain_corpus_upstream_of_ir", "status": "adjudicated_example"},
    ]

    evaluations = [
        {"id": "evaluation.oced_pg_2024", "record_type": "evaluation", "artifact_id": "artifact.oced_pg_2024", "design": "multi_dataset_demonstration", "data_or_benchmark_ids": ["supplement.oced_pg_zenodo"], "protocol": "semantic_header_to_generated_database_queries_to_event_knowledge_graph", "result": "implemented_and_demonstrated_on_seven_real_life_datasets", "effect_size": None, "uncertainty": "not_a_statistical_effect_estimate", "threats": ["mapping semantics supplied by domain knowledge", "universal source coverage not established"], "qualification_status": "research_demonstration_only"},
        {"id": "evaluation.predictive_ocpm_2022", "record_type": "evaluation", "artifact_id": "artifact.predictive_ocpm_2022", "design": "thesis_comparative_evaluation", "data_or_benchmark_ids": ["benchmark.bpic_family"], "protocol": "remaining_event_sequence_similarity_and_timestamp_MAE; exact splits pending extraction", "result": "matches_or_exceeds_prior_methods_conditioned_on_usefulness_of_selected_object_attributes", "effect_size": None, "uncertainty": "numeric_intervals_not_extracted", "threats": ["feature usefulness dependence", "thesis maturity", "target deployment shift"], "qualification_status": "target_requalification_required"},
        {"id": "evaluation.sa_ocpm_2026", "record_type": "evaluation", "artifact_id": "artifact.sa_ocpm_2026", "design": "case_study_and_method_demonstration", "data_or_benchmark_ids": ["supplement.sa_ocpm_code"], "protocol": "state derivation and transition/state-aware enrichment; full protocol pending extraction", "result": "explicit state-conditioned behavior is demonstrated", "effect_size": None, "uncertainty": "not_normalized", "threats": ["domain-specific state semantics", "case-study transportability"], "qualification_status": "research_candidate"},
        {"id": "evaluation.hnsw_2016", "record_type": "evaluation", "artifact_id": "artifact.hnsw_2016", "design": "comparative_ann_benchmark", "data_or_benchmark_ids": ["benchmark.ann_benchmarks"], "protocol": "artifact protocol; later harness is not the original experiment", "result": "effective recall-latency tradeoff reported", "effect_size": None, "uncertainty": "hardware_and_parameter_sensitive", "threats": ["dataset geometry", "distance metric", "build/search parameters", "mutation regime"], "qualification_status": "target_requalification_required"},
        {"id": "evaluation.xgboost_2016", "record_type": "evaluation", "artifact_id": "artifact.xgboost_2016", "design": "system_and_predictive_benchmarks", "data_or_benchmark_ids": [], "protocol": "primary paper protocol; normalize before comparison", "result": "scalability and model-quality results reported", "effect_size": None, "uncertainty": "confidence_intervals_not_normalized", "threats": ["task/data/tuning/hardware dependence", "predictive not causal validity"], "qualification_status": "domain_requalification_required"},
        {"id": "evaluation.btrblocks_2023", "record_type": "evaluation", "artifact_id": "artifact.btrblocks_2023", "design": "columnar_codec_benchmark", "data_or_benchmark_ids": [], "protocol": "dataset/type/hardware/configuration exact extraction pending", "result": "compression and scan tradeoffs reported", "effect_size": None, "uncertainty": "not_normalized", "threats": ["carrier type and distribution", "block size", "SIMD target", "comparison implementation"], "qualification_status": "target_requalification_required"},
    ]
    supplementary_artifacts = [
        {"id": "supplement.oced_pg_zenodo", "record_type": "supplementary_artifact", "artifact_kind": "dataset_and_semantic_headers", "research_artifact_id": "artifact.oced_pg_2024", "url": "https://doi.org/10.5281/zenodo.8296559", "version_or_digest": "Zenodo_record_8296559; file digests pending", "license": "verify_per_record_and_file", "maturity": "research_reproduction_asset"},
        {"id": "supplement.promg", "record_type": "supplementary_artifact", "artifact_kind": "source_code", "research_artifact_id": "artifact.oced_pg_2024", "url": "https://github.com/promg-dev", "version_or_digest": "exact_repository_and_commit_pending", "license": "verify_exact_repository", "maturity": "research_implementation"},
        {"id": "supplement.ocel2_schemas", "record_type": "supplementary_artifact", "artifact_kind": "validation_schemas", "research_artifact_id": "artifact.ocel2_2023", "url": "https://www.ocel-standard.org/2.0/ocel20-schema-json.json", "version_or_digest": "OCEL_2.0_JSON_schema; digest pending", "license": "verify", "maturity": "standard_validation_artifact"},
        {"id": "supplement.sa_ocpm_code", "record_type": "supplementary_artifact", "artifact_kind": "source_code_and_case_data", "research_artifact_id": "artifact.sa_ocpm_2026", "url": "https://github.com/fit-alessandro-berti/causal-model-inventory-management", "version_or_digest": "commit_pending", "license": "verify", "maturity": "research_case_study"},
        {"id": "supplement.ann_benchmarks_repo", "record_type": "supplementary_artifact", "artifact_kind": "benchmark_harness", "research_artifact_id": "artifact.ann_benchmarks_2021", "url": "https://github.com/erikbern/ann-benchmarks", "version_or_digest": "commit_and_environment_pending", "license": "verify", "maturity": "community_benchmark_harness"},
        {"id": "supplement.xgboost_repo", "record_type": "supplementary_artifact", "artifact_kind": "source_code", "research_artifact_id": "artifact.xgboost_2016", "url": "https://github.com/dmlc/xgboost", "version_or_digest": "release_or_commit_pending", "license": "Apache-2.0_candidate_verify", "maturity": "production_library"},
        {"id": "supplement.osqp_repo", "record_type": "supplementary_artifact", "artifact_kind": "source_code", "research_artifact_id": "artifact.osqp_2020", "url": "https://github.com/osqp/osqp", "version_or_digest": "release_or_commit_pending", "license": "Apache-2.0_candidate_verify", "maturity": "production_library"},
    ]
    limitations_threats = [
        {"id": stable_id("limitation", aid + "|" + limitation), "record_type": "limitation_threat", "artifact_id": aid, "text": limitation, "kind": "scope_or_validity_limit", "compiler_disposition": "refusal_or_proof_obligation_candidate"}
        for aid, detail in DEEP.items() for limitation in detail["limitations"]
    ]
    replications = [
        {"id": "replication.oced_pg_assets", "record_type": "replication", "subject_artifact_id": "artifact.oced_pg_2024", "replicating_artifact_id": None, "kind": "author_supplied_reproduction_assets", "independent": False, "status": "assets_located_execution_not_recorded", "evidence_ids": ["evidence.oced_pg_2024"]},
        {"id": "replication.ann_benchmarks_harness", "record_type": "replication", "subject_artifact_id": "artifact.hnsw_2016", "replicating_artifact_id": "artifact.ann_benchmarks_2021", "kind": "comparative_reimplementation_harness", "independent": True, "status": "protocol_and_version_must_be_bound", "evidence_ids": ["evidence.ann_benchmarks_2021"]},
        {"id": "replication.deep_corpus_queue", "record_type": "replication", "subject_artifact_id": None, "replicating_artifact_id": None, "kind": "corpus_level_gap", "independent": None, "status": "independent_replication_graph_incomplete", "evidence_ids": []},
    ]
    contradiction_supersession = [
        {"id": "adjudication.ocel_oced_parallel", "record_type": "contradiction_supersession", "subject_ids": ["artifact.ocel2_2023", "artifact.oced_core_2024"], "relation": "parallel_related_models_not_equivalent", "contradiction_status": "not_established", "supersession_status": "not_established", "reason": "different scope and maturity; compare exact core/profile/exchange semantics"},
        {"id": "adjudication.tekg_extends_temporal_representation", "record_type": "contradiction_supersession", "subject_ids": ["artifact.ekg_dimensions_2022", "artifact.tekg_2024"], "relation": "later_temporal_extension_and_transformation", "contradiction_status": "not_established", "supersession_status": "not_established", "reason": "tEKG adds snapshots/time-varying representation; original EKG questions remain addressable"},
        {"id": "adjudication.sa_ocpm_analysis_extension", "record_type": "contradiction_supersession", "subject_ids": ["artifact.ocel2_2023", "artifact.sa_ocpm_2026"], "relation": "analysis_enrichment_over_standard_data", "contradiction_status": "not_established", "supersession_status": "not_established", "reason": "state-aware enrichment depends on domain state semantics and does not silently redefine OCEL exchange identity"},
    ]
    formalisms = [
        {"id": "formalism.relational_model", "record_type": "formalism", "label": "relational model", "artifact_ids": ["artifact.codd_relational_1970"], "symbols_or_structure": "relations, tuples, domains, keys", "scope": "logical data model", "status": "candidate"},
        {"id": "formalism.selinger_search", "record_type": "formalism", "label": "costed join-order search with interesting orders", "artifact_ids": ["artifact.selinger_access_paths_1979"], "symbols_or_structure": "logical expressions, physical properties, cardinality/cost estimates", "scope": "query optimization", "status": "candidate"},
        {"id": "formalism.dataflow_time", "record_type": "formalism", "label": "event-time dataflow model", "artifact_ids": ["artifact.dataflow_2015"], "symbols_or_structure": "window, trigger, watermark, accumulation", "scope": "unbounded out-of-order data", "status": "candidate"},
        {"id": "formalism.mlir_dialect", "record_type": "formalism", "label": "MLIR dialect/operation system", "artifact_ids": ["artifact.mlir_2021"], "symbols_or_structure": "operation, region, block, value, type, attribute, rewrite", "scope": "multi-level compiler IR", "status": "candidate"},
        {"id": "formalism.ocel2", "record_type": "formalism", "label": "OCEL 2.0 metamodel", "artifact_ids": ["artifact.ocel2_2023"], "symbols_or_structure": "events, objects, types, qualified E2O/O2O relations, time-varying attributes", "scope": "object-centric event-data exchange", "status": "candidate"},
        {"id": "formalism.tekg", "record_type": "formalism", "label": "temporal event knowledge graph", "artifact_ids": ["artifact.tekg_2024"], "symbols_or_structure": "events, entities, snapshots, temporal relations, directly-follows edges", "scope": "temporal graph representation of OCEL 2.0", "status": "candidate"},
        {"id": "formalism.state_aware_ocpm", "record_type": "formalism", "label": "state-aware OCPM state model", "artifact_ids": ["artifact.sa_ocpm_2026"], "symbols_or_structure": "state set, object×time state function, transition event, state-aware label", "scope": "domain-conditioned process analysis", "status": "candidate"},
        {"id": "formalism.differential_privacy", "record_type": "formalism", "label": "differential privacy adjacency and mechanism", "artifact_ids": ["artifact.differential_privacy_2006"], "symbols_or_structure": "adjacent datasets, sensitivity, epsilon, output distributions", "scope": "privacy guarantee", "status": "candidate"},
        {"id": "formalism.provenance_semiring", "record_type": "formalism", "label": "provenance semiring", "artifact_ids": ["artifact.semiring_provenance_2007"], "symbols_or_structure": "K-relations, addition, multiplication, annotations", "scope": "positive relational query provenance", "status": "candidate"},
        {"id": "formalism.quadratic_program", "record_type": "formalism", "label": "convex quadratic program", "artifact_ids": ["artifact.osqp_2020"], "symbols_or_structure": "quadratic objective, linear constraints, residuals, certificates", "scope": "prescriptive optimization", "status": "candidate"},
    ]
    semantic_types = [
        {"id": "research_type.event_identity", "record_type": "research_type", "label": "event identity", "artifact_ids": ["artifact.ocel2_2023", "artifact.ekg_dimensions_2022"], "equality": "profile_and_domain_defined", "invalidity": "missing_or_colliding_identity"},
        {"id": "research_type.object_identity", "record_type": "research_type", "label": "object/entity identity", "artifact_ids": ["artifact.ocel2_2023", "artifact.oced_core_2024"], "equality": "domain_and_profile_defined", "invalidity": "unresolved_or_scope_ambiguous"},
        {"id": "research_type.qualified_event_object_relation", "record_type": "research_type", "label": "qualified event-to-object relation", "artifact_ids": ["artifact.ocel2_2023"], "equality": "event+object+qualifier+profile", "invalidity": "unknown_qualifier_semantics"},
        {"id": "research_type.time_varying_attribute", "record_type": "research_type", "label": "time-varying object attribute", "artifact_ids": ["artifact.ocel2_2023", "artifact.tekg_2024"], "equality": "object+attribute+valid_time+value_semantics", "invalidity": "overlap_or_missing_time_policy"},
        {"id": "research_type.domain_state_function", "record_type": "research_type", "label": "domain state function", "artifact_ids": ["artifact.sa_ocpm_2026"], "equality": "owner+object_type+time_domain+state_set+rule_edition", "invalidity": "ambiguous_or_unqualified_state_derivation"},
        {"id": "research_type.prediction_task", "record_type": "research_type", "label": "prediction task", "artifact_ids": ["artifact.predictive_ocpm_2022", "artifact.xgboost_2016"], "equality": "target+population+unit+cutoff+horizon+loss", "invalidity": "leakage_or_undefined_target"},
        {"id": "research_type.prediction_result", "record_type": "research_type", "label": "prediction result", "artifact_ids": ["artifact.predictive_ocpm_2022"], "equality": "task+model_occurrence+subject+decision_time+horizon", "invalidity": "expired_or_missing_lineage"},
        {"id": "research_type.prediction_set", "record_type": "research_type", "label": "conformal prediction set", "artifact_ids": ["artifact.conformal_prediction_2005"], "equality": "task+calibration_occurrence+alpha+subject", "invalidity": "assumption_or_calibration_scope_failure"},
        {"id": "research_type.estimand", "record_type": "research_type", "label": "estimand", "artifact_ids": ["artifact.double_ml_2018"], "equality": "population+treatment+outcome+contrast+time", "invalidity": "undefined_or_unidentified"},
        {"id": "research_type.estimator", "record_type": "research_type", "label": "estimator", "artifact_ids": ["artifact.double_ml_2018"], "equality": "estimand+procedure+data_split+nuisance_contract", "invalidity": "assumptions_or_fit_failure"},
        {"id": "research_type.algorithm_qualification", "record_type": "research_type", "label": "algorithm target qualification", "artifact_ids": ["artifact.hnsw_2016", "artifact.osqp_2020"], "equality": "algorithm+implementation+target+workload+configuration", "invalidity": "unexecuted_or_stale"},
        {"id": "research_type.benchmark_occurrence", "record_type": "research_type", "label": "benchmark occurrence", "artifact_ids": ["artifact.ann_benchmarks_2021"], "equality": "suite+commit+data+split+hardware+software+config+protocol", "invalidity": "missing_receipt"},
    ]
    models = [
        {"id": "model.kalman_state_space", "record_type": "model", "label": "linear Gaussian state-space model", "artifact_ids": ["artifact.kalman_1960"], "model_kind": "probabilistic_dynamic", "fit_state": "model_family_not_fitted_artifact"},
        {"id": "model.cox_proportional_hazards", "record_type": "model", "label": "Cox proportional-hazards model", "artifact_ids": ["artifact.cox_1972"], "model_kind": "survival_regression", "fit_state": "model_family_not_fitted_artifact"},
        {"id": "model.gradient_boosted_trees", "record_type": "model", "label": "regularized gradient-boosted tree ensemble", "artifact_ids": ["artifact.xgboost_2016", "artifact.lightgbm_2017"], "model_kind": "supervised_predictive", "fit_state": "model_family_not_fitted_artifact"},
        {"id": "model.nhits", "record_type": "model", "label": "N-HiTS hierarchical interpolation forecasting model", "artifact_ids": ["artifact.nhits_2022"], "model_kind": "time_series_forecasting", "fit_state": "model_family_not_fitted_artifact"},
        {"id": "model.patchtst", "record_type": "model", "label": "PatchTST time-series forecasting model", "artifact_ids": ["artifact.patchtst_2023"], "model_kind": "non_LLM_time_series_transformer", "fit_state": "model_family_not_fitted_artifact"},
        {"id": "model.predictive_ocpm_sequence", "record_type": "model", "label": "object-centric process sequence prediction model", "artifact_ids": ["artifact.predictive_ocpm_2022"], "model_kind": "sequence_prediction_pipeline", "fit_state": "artifact_family_not_production_model"},
    ]
    estimators = [
        {"id": "estimator.kalman_filter", "record_type": "estimator", "label": "Kalman filtering recursion", "artifact_ids": ["artifact.kalman_1960"], "estimand_or_target": "latent state conditional estimate", "assumption_status": "must_be_declared"},
        {"id": "estimator.xgboost_fit", "record_type": "estimator", "label": "XGBoost regularized boosting fit", "artifact_ids": ["artifact.xgboost_2016"], "estimand_or_target": "task-dependent predictive risk minimizer", "assumption_status": "must_be_declared"},
        {"id": "estimator.double_ml_crossfit", "record_type": "estimator", "label": "cross-fitted orthogonal-score estimator", "artifact_ids": ["artifact.double_ml_2018"], "estimand_or_target": "declared causal/structural parameter", "assumption_status": "identification_and_rate_conditions_required"},
        {"id": "estimator.split_conformal", "record_type": "estimator", "label": "split-conformal calibration procedure", "artifact_ids": ["artifact.conformal_prediction_2005"], "estimand_or_target": "marginal prediction-set coverage", "assumption_status": "exchangeability_or_variant_contract_required"},
        {"id": "estimator.ocpm_sequence", "record_type": "estimator", "label": "predictive OCPM sequence/timestamp fit", "artifact_ids": ["artifact.predictive_ocpm_2022"], "estimand_or_target": "remaining activity sequence and event time", "assumption_status": "task_and_log_construction_required"},
    ]
    guarantees = [
        {"id": "guarantee.conformal_marginal_coverage", "record_type": "guarantee", "artifact_ids": ["artifact.conformal_prediction_2005"], "statement": "marginal coverage under the selected conformal procedure's assumptions", "assumptions": ["exchangeability_or_explicit_variant_replacement"], "not_guaranteed": ["conditional_coverage", "coverage_under_arbitrary_shift"]},
        {"id": "guarantee.differential_privacy", "record_type": "guarantee", "artifact_ids": ["artifact.differential_privacy_2006"], "statement": "bounded output-distribution change for adjacent datasets", "assumptions": ["adjacency", "sensitivity", "mechanism", "composition_scope"], "not_guaranteed": ["correct_analysis", "authorization", "side_channel_absence"]},
        {"id": "guarantee.provenance_composition", "record_type": "guarantee", "artifact_ids": ["artifact.semiring_provenance_2007"], "statement": "compositional annotation propagation for the supported query/algebra scope", "assumptions": ["positive_relational_fragment", "semiring_laws"], "not_guaranteed": ["physical_lineage_capture", "all_query_languages"]},
        {"id": "guarantee.hnsw_empirical_tradeoff", "record_type": "guarantee", "artifact_ids": ["artifact.hnsw_2016"], "statement": "empirical recall-latency tradeoff, not universal exactness", "assumptions": ["distance", "data_geometry", "parameters", "target"], "not_guaranteed": ["exact_nearest_neighbor", "target_independent_performance"]},
        {"id": "guarantee.osqp_status_scoped", "record_type": "guarantee", "artifact_ids": ["artifact.osqp_2020"], "statement": "solver status/certificates within supported convex QP and tolerance/numerical scope", "assumptions": ["canonical_form", "convexity", "numerical_tolerances"], "not_guaranteed": ["business_feasibility_from_vector_alone", "global_nonconvex_optimum"]},
    ]

    relation_ontology = [
        {"id": "relation_type." + k, "record_type": "relation_type", "label": k, "from_kind": f, "to_kind": t, "law": law}
        for k, f, t, law in RELATION_TYPES
    ]
    conversion_rules = [
        {"id": "conversion_rule." + k, "record_type": "conversion_rule", "law": law, "severity": "constitutional", "enforcement": "validator_or_adjudication_gate"}
        for k, law in CONVERSION_RULES
    ]

    gaps = [
        {"id": "gap.full_text_extraction", "record_type": "gap", "severity": "high", "description": "Metadata-only candidates lack normalized full-text claim/protocol/result/limitation extraction.", "closure": "primary full-text extraction with page/section locators and independent review"},
        {"id": "gap.contributor_identifiers", "record_type": "gap", "severity": "high", "description": "Names are not yet resolved to ORCID/OpenAlex/DBLP identities and historical affiliations.", "closure": "identifier resolution without name-only merge; retain occurrence affiliation"},
        {"id": "gap.replication_graph", "record_type": "gap", "severity": "high", "description": "Independent replications, negative results, retractions, and superseding editions are sparse.", "closure": "citation-neighborhood review by claim and benchmark, not popularity"},
        {"id": "gap.predictive_taxonomy", "record_type": "gap", "severity": "high", "description": "Predictive analytics needs deeper coverage of survival, competing risks, count, hierarchical, intermittent, probabilistic, spatial-temporal, graph, anomaly, maintenance, and decision-aware prediction.", "closure": "separate method-family research wave with target/horizon/loss/uncertainty/drift contracts"},
        {"id": "gap.cs_saturation", "record_type": "gap", "severity": "constitutional", "description": "All computer science and applied mathematics cannot be enumerated as a closed list.", "closure": "governed extension, coverage cells, novelty queue, and saturation metrics by question/concept/method/target"},
        {"id": "gap.license_ip", "record_type": "gap", "severity": "high", "description": "Paper access, code license, dataset license, patent/IP, and generated implementation rights are not equivalent.", "closure": "exact artifact/version license and IP adjudication before library contribution"},
        {"id": "gap.product_evidence", "record_type": "gap", "severity": "medium", "description": "Research efficacy does not establish enterprise product demand, operability, supportability, or economics.", "closure": "separate product/market/operational qualification evidence"},
    ]

    schemas = {
        "node.schema.json": {"$schema": "https://json-schema.org/draft/2020-12/schema", "title": "Research artifact graph node", "type": "object", "required": ["id", "record_type"], "properties": {"id": {"type": "string", "minLength": 3}, "record_type": {"enum": ["work", "edition", "venue_occurrence", "artifact", "person", "institution", "contribution", "source", "evidence", "concept", "formalism", "research_type", "claim", "method", "model", "estimator", "algorithm", "guarantee", "implementation", "benchmark", "evaluation", "supplementary_artifact", "limitation_threat", "replication", "contradiction_supersession", "compiler_mapping", "conversion_rule", "review_item", "gap", "conflict_replication_case", "relation_type"]}}, "additionalProperties": True},
        "relation.schema.json": {"$schema": "https://json-schema.org/draft/2020-12/schema", "title": "Research artifact graph relation", "type": "object", "required": ["id", "record_type", "relation_type", "from_id", "to_id", "evidence_id"], "properties": {"id": {"type": "string"}, "record_type": {"const": "relation"}, "relation_type": {"type": "string"}, "from_id": {"type": "string"}, "to_id": {"type": "string"}, "evidence_id": {"type": "string"}}, "additionalProperties": True},
        "artifact.schema.json": {"$schema": "https://json-schema.org/draft/2020-12/schema", "title": "Research artifact", "type": "object", "required": ["id", "record_type", "kind", "category", "year", "title", "primary_url", "version", "extraction_status", "non_llm"], "properties": {"id": {"type": "string", "pattern": "^artifact\\."}, "record_type": {"const": "artifact"}, "year": {"type": "integer", "minimum": 1800, "maximum": 2026}, "non_llm": {"const": True}, "extraction_status": {"enum": ["metadata_only", "partial", "deep"]}}, "additionalProperties": True},
    }

    datasets = {
        "works.jsonl": works, "editions.jsonl": editions, "venue-occurrences.jsonl": venue_occurrences,
        "artifacts.jsonl": artifacts, "people.jsonl": list(people.values()), "institutions.jsonl": institutions,
        "contributions.jsonl": contributions, "sources.jsonl": sources, "evidence.jsonl": evidence,
        "concepts.jsonl": concepts, "claims.jsonl": claims, "methods.jsonl": methods,
        "formalisms.jsonl": formalisms, "research-types.jsonl": semantic_types,
        "models.jsonl": models, "estimators.jsonl": estimators, "guarantees.jsonl": guarantees,
        "algorithms.jsonl": algorithms, "implementations.jsonl": implementations, "benchmarks.jsonl": benchmarks,
        "relations.jsonl": relations, "relation-ontology.jsonl": relation_ontology,
        "evaluations.jsonl": evaluations, "supplementary-artifacts.jsonl": supplementary_artifacts,
        "limitations-threats.jsonl": limitations_threats, "replications.jsonl": replications,
        "contradictions-supersessions.jsonl": contradiction_supersession,
        "compiler-library-mappings.jsonl": mappings, "conversion-rules.jsonl": conversion_rules,
        "conflict-replication.jsonl": conflict_replication, "review-queue.jsonl": reviews, "gaps.jsonl": gaps,
    }
    for name, rows in datasets.items():
        write_jsonl(name, rows)
    for name, schema in schemas.items():
        write_json("schemas/" + name, schema)

    categories = Counter(a["category"] for a in artifacts)
    manifest = {
        "id": "manifest.research_artifact_graph.v0_1_0", "edition": "0.1.0-candidate",
        "generated_on": AS_OF, "deterministic_source": "build_corpus.py",
        "constitutional_posture": "open_world_governed_extension",
        "counts": {name: len(rows) for name, rows in datasets.items()},
        "coverage": {
            "artifact_categories": dict(sorted(categories.items())),
            "artifacts_total": len(artifacts),
            "foundational_le_2020": sum(a["foundational"] for a in artifacts),
            "recent_2021_2026": sum(a["recent"] for a in artifacts),
            "deep_extractions": sum(a["extraction_status"] == "deep" for a in artifacts),
            "primary_source_records": len(sources), "non_llm_artifacts": sum(a["non_llm"] for a in artifacts),
        },
        "saturation_law": "No finite corpus is all CS. Coverage is measured over declared category×artifact-kind×evidence-depth×compiler-mapping cells; new artifacts enter a review queue and cannot silently mutate canonical concepts.",
        "files": sorted(datasets) + ["schemas/artifact.schema.json", "schemas/node.schema.json", "schemas/relation.schema.json"],
    }
    write_json("manifest.json", manifest)
    write_json("metamodel.json", {
        "id": "metamodel.research_artifact_graph.v0_1_0",
        "identity_ladder": ["work", "edition", "venue_occurrence", "artifact", "claim", "concept", "method", "algorithm", "implementation", "benchmark_run", "deployment_occurrence"],
        "evidence_dimensions": ["source", "locator", "scope", "claim", "assumptions", "population", "protocol", "metric", "result", "uncertainty", "limitation", "replication", "contradiction", "supersession"],
        "conversion_dimensions": ["practice", "method", "operation", "representation", "algorithm", "kernel", "library", "compiler_phase", "product_capability", "target_qualification"],
        "never_collapse": ["paper_with_claim", "claim_with_concept", "method_with_algorithm", "algorithm_with_implementation", "benchmark_with_qualification", "author_with_inventor", "citation_with_authorship", "standard_with_serialization", "model_score_with_domain_validity"],
    })


if __name__ == "__main__":
    generate()
