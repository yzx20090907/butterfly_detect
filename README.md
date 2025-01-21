废话不多说直接上图

![](https://cdn.nlark.com/yuque/0/2025/png/38622944/1737439636540-236667d0-3103-43b5-8428-579893ffc907.png?x-oss-process=image%2Fresize%2Cw_1500%2Climit_0)

# 功能如下
+ 63种蝴蝶种类识别
+ 识别记录持久保存（关闭软件也可用）
+ ~~优美的客户端，精美的动画~~

## 怎么让项目Run起来？
1. 安装依赖

```plain
pip install -r requirements.txt
```

2. 启动ui

```plain
python ui.py
```

3. （可选）删除json文件

选择图片玩耍吧~

### 文件夹介绍
1. ok文件夹内为识别准确率80%以上的图片
2. all_photo文件夹为训练时划分出的测试集
3. result文件夹为识别结果暂存文件夹

## 训练结果


## 支持识别的蝴蝶种类
```yaml
- Atrophaneura_varuna
- Byasa_alcinous
- Graphium_agamemnon
- Graphium_cloanthus
- Graphium_sarpedon
- Iphiclides_podalirius
- Lamproptera_curius
- Lamproptera_meges
- Meandrusa_payeni
- Meandrusa_sciron
- Pachliopta_aristolochiae
- Pathysa_antiphates
- Pazala_eurous
- Teinopalpus_aureus
- Teinopalpus_imperialis
- Troides_helena
- Troides_aeacus
- Bhutanitis_lidderdalii
- Sericinus_montelus
- Parnassius_apollo
- Parnassius_nomion
- Parnassius_phoebus
- Catopsilia_pomona
- Catopsilia_pyranthe
- Catopsilia_scylla
- Colias_erate
- Colias_fieldii
- Eurema_blanda
- Eurema_andersoni
- Eurema_brigitta
- Eurema_hecabe
- Eurema_laeta
- Gonepteryx_rhamni
- Apatura_iris
- Chitoria_ulupi
- Hestina_assimilis
- Rohana_parisatis
- Ariadne_ariadne
- Euthalia_niepelti
- Athyma_perius
- Limenitis_sulpitia
- Neptis_hylas
- Cyrestis_thyodamas
- Stibochiona_nicea
- Allotinus_drumila
- Miletus_chinensis
- Taraka_hamada
- Curetis_acuta
- Arhopala_paramuta
- Arhopala_rama
- Artipe_eryx
- Horaga_albimacula
- Horaga_onyx
- Ampittia_virgata
- Ancistroides_nigrita
- Astictopterus_jama
- Erionota_torus
- Iambrix_salsala
- Isoteinon_lamprospilus
- Parnara_guttata
- Notocrypta_curvifascia
- Udaspes_folus
- Seseria_dohertyi
```

