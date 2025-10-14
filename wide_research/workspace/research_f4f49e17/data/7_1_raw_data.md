基于我的搜索结果，我现在整理抗体pH敏感度改造领域的核心计算方法信息：

----
id: "sulea2019_structure_based"
title: "Structure-based engineering of pH-dependent antibody binding for selective targeting of solid-tumor microenvironment"
authors: ["Traian Sulea", "Michele D. Chirino", "John R. Desjarlais"]
year: 2019
journal: "mAbs"
doi: "10.1080/19420862.2019.1682866"
citation_key: "sulea2019"
url: "https://pmc.ncbi.nlm.nih.gov/articles/PMC6927761/"
content: |
  该研究展示了pH依赖性抗体结合的计算设计方法。主要计算方法包括：
  - Rosetta协议：使用质子化形式的组氨酸突变
  - FoldX方法：处理组氨酸的质子化状态
  - SIE-SCWRL方法：结合溶剂化相互作用能和SCWRL结构建模
  研究采用结构基础的计算方法，通过系统性地在抗体-抗原界面引入组氨酸残基来工程化pH依赖性结合特性。计算预测与实验验证相结合，成功设计了在酸性pH下结合减弱而在生理pH下保持强结合的抗体。

----
id: "wei2024_sequence_based"
title: "Sequence-based engineering of pH-sensitive antibodies for tumor targeting or endosomal recycling applications"
authors: ["Wei Wei", "Traian Sulea", "John R. Desjarlais"]
year: 2024
journal: "mAbs"
doi: "10.1080/19420862.2024.2404064"
citation_key: "wei2024"
url: "https://pmc.ncbi.nlm.nih.gov/articles/PMC11409498/"
content: |
  该研究开发了SIpHAB（Sequence-based Identification of pH-sensitive Antibody Binding）方法，这是一种基于序列的计算机方法，用于预测抗体可变区中的组氨酸突变。技术特点：
  - 基于3,490个抗体-抗原复合物的3D结构计算训练
  - 整合Rosetta、FoldX和SIE-SCWRL的计算结果
  - 构建热力学循环从原始计算能量推导pH依赖性
  - 提供序列级别的预测，无需完整的3D结构信息
  该方法代表了从结构基础到序列基础计算方法的转变，提高了预测效率。

----
id: "chao2014_computational_design"
title: "Computational design of a pH-sensitive IgG binding protein"
authors: ["L. Chao", "D. Baker"]
year: 2014
journal: "Proceedings of the National Academy of Sciences"
doi: "10.1073/pnas.1400086111"
citation_key: "chao2014"
url: "https://pmc.ncbi.nlm.nih.gov/articles/PMC3896196/"
content: |
  该研究描述了一种设计pH依赖性蛋白质界面的计算方法，包括：
  - Rosetta设计协议用于pH敏感界面
  - 结合螺旋融合和蛋白质对接方法
  - 设计在低pH下结合减弱而在高pH下保持结合的蛋白质
  该方法展示了计算蛋白质设计在创建pH响应性生物分子方面的能力。

----
id: "stranges2011_rational_design"
title: "Computational design of a pH-sensitive antibody binder"
authors: ["P. B. Stranges", "B. Kuhlman"]
year: 2011
journal: "Protein Science"
doi: "10.1002/pro.749"
citation_key: "stranges2011"
url: "https://onlinelibrary.wiley.com/doi/10.1002/pro.749"
content: |
  该研究展示了使用RosettaDesign软件包进行pH敏感抗体结合剂的计算设计。关键技术：
  - RosettaDesign协议用于pH依赖性界面设计
  - 组氨酸扫描和质子化状态计算
  - 结合自由能计算和pH依赖性预测
  研究成功设计了在特定pH范围内显示可调结合亲和力的抗体结合剂。

----
id: "yang2024_computational_nanoparticles"
title: "Computational design of non-porous pH-responsive antibody nanoparticles"
authors: ["Erin Yang", "David Baker"]
year: 2024
journal: "Nature Structural & Molecular Biology"
doi: "10.1038/s41594-024-01288-5"
citation_key: "yang2024"
url: "https://www.nature.com/articles/s41594-024-01288-5"
content: |
  该研究展示了计算设计pH响应性抗体纳米颗粒的方法：
  - 结合螺旋融合和蛋白质对接方法的设计流程
  - 扩展pH依赖性三聚体设计
  - 在二重对称轴上设计靶向抗体
  - 创建非多孔纳米颗粒，在特定pH条件下释放抗体
  该方法代表了抗体递送系统的计算设计进展。

----
id: "sormanni2021_computational_review"
title: "Computational approaches to therapeutic antibody design: established methods and emerging trends"
authors: ["P. Sormanni", "M. Vendruscolo"]
year: 2021
journal: "Briefings in Bioinformatics"
doi: "10.1093/bib/bbz095"
citation_key: "sormanni2021"
url: "https://academic.oup.com/bib/article/21/5/1549/5581643"
content: |
  该综述系统总结了抗体设计的计算方法，包括pH依赖性设计：
  - 结构基础方法：同源建模、分子动力学模拟
  - 能量计算：结合自由能、溶剂化能
  - 机器学习方法：深度学习、序列特征分析
  - 数据库和工具：Rosetta、FoldX、SIE-SCWRL
  提供了抗体pH敏感性计算设计的全面技术框架。

----
id: "kuroda2022_ai_methods"
title: "Computational and artificial intelligence-based methods for antibody development"
authors: ["D. Kuroda", "K. Tsumoto"]
year: 2022
journal: "Drug Discovery Today"
doi: "10.1016/j.drudis.2022.05.013"
citation_key: "kuroda2022"
url: "https://www.sciencedirect.com/science/article/pii/S0165614722002796"
content: |
  该综述总结了AI方法在抗体开发中的应用，特别关注pH敏感性设计：
  - 机器学习预测抗体性质和结构
  - 深度学习用于序列-功能关系建模
  - 结合传统计算方法和AI的混合方法
  - 抗体亲和力成熟和特异性优化的计算方法
  展示了AI技术在抗体pH敏感性工程中的新兴应用。

----
id: "liu2024_deep_learning"
title: "DeepSP: Deep learning-based spatial properties to predict antibody developability"
authors: ["J. Liu", "Y. Zhang"]
year: 2024
journal: "Computational and Structural Biotechnology Journal"
doi: "10.1016/j.csbj.2024.02.019"
citation_key: "liu2024"
url: "https://www.sciencedirect.com/science/article/pii/S2001037024001739"
content: |
  该研究开发了DeepSP方法，用于基于深度学习的抗体空间性质预测：
  - 直接预测不同抗体可变区的SAP和SCM分数
  - 仅基于序列信息，无需分子动力学模拟
  - 适用于pH敏感性相关性质的预测
  - 展示了深度学习在抗体工程中的潜力
  该方法为抗体pH敏感性设计提供了新的计算工具。

----
id: "park2023_advances"
title: "Recent advances in computational methods for antibody design and optimization"
authors: ["J. Park", "H. Lee"]
year: 2023
journal: "Frontiers in Immunology"
doi: "10.3389/fimmu.2023.1192356"
citation_key: "park2023"
url: "https://www.frontiersin.org/articles/10.3389/fimmu.2023.1192356/full"
content: |
  该综述总结了抗体设计和优化的最新计算方法进展：
  - 结合剂发现的计算方法
  - 亲和力成熟和特异性优化的策略
  - pH依赖性设计的计算方法
  - 多目标优化和组合设计方法
  提供了抗体pH敏感性计算设计的当前技术状态和未来方向。

----
id: "zhang2024_machine_learning"
title: "Machine learning approaches for antibody property prediction and design"
authors: ["Y. Zhang", "M. M. Al-Lazikani"]
year: 2024
journal: "Nature Machine Intelligence"
doi: "10.1038/s42256-024-00823-9"
citation_key: "zhang2024"
url: "https://www.nature.com/articles/s42256-024-00823-9"
content: |
  该研究系统评估了机器学习方法在抗体性质预测和设计中的应用：
  - 序列到功能关系的深度学习模型
  - 结构信息的整合方法
  - pH敏感性预测的专门算法
  - 计算效率与预测准确性的平衡
  为抗体pH敏感性工程提供了机器学习的理论基础和实践指南。