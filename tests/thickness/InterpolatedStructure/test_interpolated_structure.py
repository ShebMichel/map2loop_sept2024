# This test runs on a portion of the dataset in https://github.com/Loop3D/m2l3_examples/tree/main/Laurent2016_V2_variable_thicknesses (only for lithologies E, F, and G)
# structures are confined to litho_F, and the test confirms if the StructuralPoint thickness is calculated, for all lithologies, if the thickness is correct for F (~90 m), and top/bottom units are assigned -1
# this creates a temp folder in Appdata to store the data to run the proj, checks the thickness, and then deletes the temp folder
# this was done to avoid overflow of file creation in the tests folder

### This file tests the function InterpolatedStructure thickness calculator

import pytest
import pandas as pd
import numpy as np
from map2loop.thickness_calculator import InterpolatedStructure
from map2loop.project import Project
from osgeo import gdal, osr
import os
import shapely
import geopandas
import tempfile
import pathlib
from map2loop.sampler import SamplerSpacing, SamplerDecimator
from map2loop.m2l_enums import Datatype
import map2loop


def create_raster(output_path, bbox, epsg, pixel_size, value=100):
    minx, miny, maxx, maxy = bbox
    cols = int((maxx - minx) / pixel_size)
    rows = int((maxy - miny) / pixel_size)
    driver = gdal.GetDriverByName('GTiff')
    out_raster = driver.Create(output_path, cols, rows, 1, gdal.GDT_Byte)
    out_raster.SetGeoTransform([minx, pixel_size, 0, maxy, 0, -pixel_size])
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(epsg)
    out_raster.SetProjection(srs.ExportToWkt())
    out_band = out_raster.GetRasterBand(1)
    out_band.Fill(value)
    out_band.FlushCache()
    out_raster = None


geology = [
    {
        'UNITNAME': 'Litho_E',
        'geometry': 'POLYGON ((9795.91836734694 9931.26849738919, 9860.73785898637 9795.91836734694, 9935.33621028978 9591.836734693878, 9950.618354641661 9387.755102040817, 10000 9210.342095822705, 10000 8757.661313426739, 9957.613263811385 8571.428571428572, 9795.91836734694 8453.228230379065, 9591.836734693878 8459.27180076132, 9387.755102040817 8424.58063242387, 9183.673469387755 8396.186050103635, 8979.591836734695 8375.328219666773, 8775.510204081633 8142.6900746871015, 8533.835897640307 7959.183673469388, 8367.34693877551 7832.006337691327, 8271.702357700893 7755.102040816327, 8163.265306122449 7660.1472192881065, 8074.276982521525 7551.0204081632655, 7959.183673469388 7424.887053820552, 7876.85861392897 7346.938775510204, 7755.102040816327 7225.488935198103, 7672.260829380581 7142.857142857143, 7551.0204081632655 7021.922675930724, 7447.64756183235 6938.775510204082, 7346.938775510204 6858.865387585699, 7149.179419692682 6734.693877551021, 6938.775510204082 6628.052847726005, 6734.693877551021 6533.238936443719, 6530.6122448979595 6522.261950434471, 6326.530612244898 6520.453083271883, 6122.448979591837 6525.756680235571, 5918.367346938776 6543.242785395409, 5714.285714285715 6570.203352947625, 5510.2040816326535 6597.437955895249, 5306.122448979592 6623.455748266104, 5102.040816326531 6558.673625089685, 5021.544086689852 6530.6122448979595, 4897.95918367347 6484.284692881059, 4648.165410878707 6326.530612244898, 4456.931912169165 6122.448979591837, 4285.714285714286 5949.72882952009, 4081.6326530612246 5747.855828732861, 3877.5510204081634 5481.342782779616, 3673.469387755102 5299.687677500199, 3469.387755102041 5113.124847412109, 3233.5997600944675 4897.95918367347, 3061.2244897959185 4761.364995216837, 2978.9564560870735 4693.877551020409, 2857.1428571428573 4509.9974651725925, 2727.7656477324817 4285.714285714286, 2653.061224489796 4194.911256128428, 2620.9440036695833 4081.6326530612246, 2653.061224489796 3834.8668935347578, 2714.296846973653 3673.469387755102, 2767.1924902468313 3469.387755102041, 2857.1428571428573 3316.1486411581236, 2932.2801317487447 3265.3061224489797, 3061.2244897959185 3201.1586792615, 3265.3061224489797 3115.340836194097, 3411.8516104561945 3061.2244897959185, 3469.387755102041 3039.713489766024, 3673.469387755102 2953.3901993109257, 3877.5510204081634 2900.4941667829244, 4081.6326530612246 2919.088869678731, 4285.714285714286 2942.9248887665417, 4489.795918367347 2963.555199759347, 4693.877551020409 2917.314840822804, 4809.648941974251 2857.1428571428573, 4897.95918367347 2811.5255005505624, 5102.040816326531 2712.551039092395, 5243.474220742985 2653.061224489796, 5306.122448979592 2627.6203077666614, 5510.2040816326535 2402.532733216578, 5649.461551588409 2244.8979591836737, 5714.285714285715 2173.8852286825377, 5838.211215272242 2040.8163265306123, 5918.367346938776 1953.0603836993782, 6037.69419144611 1836.734693877551, 6122.448979591837 1756.0881011340084, 6277.958616918448 1632.6530612244899, 6326.530612244898 1595.732338574468, 6532.909626863441 1428.5714285714287, 6734.693877551021 1276.012440117038, 6876.561690349969 1224.4897959183675, 6938.775510204082 1201.8953050885882, 7142.857142857143 1139.765856217365, 7346.938775510204 1082.3855108144332, 7551.0204081632655 1067.0050796197386, 7755.102040816327 1078.0507691052496, 7995.249689841758 1020.4081632653061, 8163.265306122449 949.2362275415538, 8367.34693877551 868.0756238042093, 8499.189882862325 816.3265306122449, 8571.428571428572 789.4330608601473, 8775.510204081633 723.8424554163096, 8902.20797791773 612.2448979591837, 8979.591836734695 360.74278305987923, 8979.591836734695 180.16181430038142, 8858.95553900271 0, 6046.468258728215 0, 5863.85825506431 296.3535950262776, 5435.566874501761 724.6449755888261, 5282.605667157994 908.1984244013456, 4900.202648798577 1122.3441146826208, 4638.256581222377 1168.2324768857502, 4454.703132409856 1154.8483712431703, 4190.845049741858 1118.520084499026, 3988.1714500113685 1181.6165825283297, 3642.0967183960943 1311.6336087705313, 3024.5158437456353 1594.6118423565003, 2573.2802820815227 1816.4055930049626, 2175.581142987729 2107.0318869581197, 1831.4184264642531 2558.267448622232, 1380.1828648001406 2910.078225512896, 531.2481640422343 3177.7603383644882, 0 3187.497507640264, 0 4970.218705429992, 78.1005872863268 5095.511475436967, 303.71836811838307 5355.545527921371, 739.6578090481191 5745.596606647977, 904.0911069426686 5887.085723440961, 1297.9662158528683 6024.750810050351, 1787.4420793529227 6116.527534456612, 2169.8450977123402 6135.647685374583, 2498.711693501439 6185.3600777613065, 3003.4836777358705 6261.84068143319, 3485.311480868737 6430.098009511334, 3798.881955923459 6705.428182730114, 4250.1175175875715 7240.792408433298, 4731.945320720438 7638.491547527093, 5297.901787892375 7982.654264050569, 5802.673772126806 8112.67129029277, 6276.853514892484 8303.87279947248, 6712.79295582222 8609.795214160013, 6896.346404634739 8785.700602605346, 6995.771189408188 8969.254051417865, 6942.234766837869 9206.343922800705, 6766.329378392537 9558.154699691368, 6414.518601501873 9986.446080253916, 6402.234572809949 10000, 9765.614100864956 10000, 9795.91836734694 9931.26849738919))',
        'GROUP': 'A',
        'ID': 0,
    },
    {
        'UNITNAME': 'Litho_F',
        'geometry': 'MULTIPOLYGON (((8979.591836734695 360.74278305987923, 8902.20797791773 612.2448979591837, 8775.510204081633 723.8424554163096, 8571.428571428572 789.4330608601473, 8499.189882862325 816.3265306122449, 8367.34693877551 868.0756238042093, 8163.265306122449 949.2362275415538, 7995.249689841758 1020.4081632653061, 7755.102040816327 1078.0507691052496, 7551.0204081632655 1067.0050796197386, 7346.938775510204 1082.3855108144332, 7142.857142857143 1139.765856217365, 6938.775510204082 1201.8953050885882, 6876.561690349969 1224.4897959183675, 6734.693877551021 1276.012440117038, 6532.909626863441 1428.5714285714287, 6326.530612244898 1595.732338574468, 6277.958616918448 1632.6530612244899, 6122.448979591837 1756.0881011340084, 6037.69419144611 1836.734693877551, 5918.367346938776 1953.0603836993782, 5838.211215272242 2040.8163265306123, 5714.285714285715 2173.8852286825377, 5649.461551588409 2244.8979591836737, 5510.2040816326535 2402.532733216578, 5306.122448979592 2627.6203077666614, 5243.474220742985 2653.061224489796, 5102.040816326531 2712.551039092395, 4897.95918367347 2811.5255005505624, 4809.648941974251 2857.1428571428573, 4693.877551020409 2917.314840822804, 4489.795918367347 2963.555199759347, 4285.714285714286 2942.9248887665417, 4081.6326530612246 2919.088869678731, 3877.5510204081634 2900.4941667829244, 3673.469387755102 2953.3901993109257, 3592.122504199657 2987.798639529117, 3469.387755102041 3039.713489766024, 3411.8516104561945 3061.2244897959185, 3265.3061224489797 3115.340836194097, 3061.2244897959185 3201.1586792615, 2932.2801317487447 3265.3061224489797, 2857.1428571428573 3316.1486411581236, 2767.1924902468313 3469.387755102041, 2714.296846973653 3673.469387755102, 2653.061224489796 3834.8668935347578, 2620.9440036695833 4081.6326530612246, 2653.061224489796 4194.911256128428, 2727.7656477324817 4285.714285714286, 2857.1428571428573 4509.9974651725925, 2978.9564560870735 4693.877551020409, 3061.2244897959185 4761.364995216837, 3233.5997600944675 4897.95918367347, 3469.387755102041 5113.124847412109, 3673.469387755102 5299.687677500199, 3877.5510204081634 5481.342782779616, 4081.6326530612246 5747.855828732861, 4285.714285714286 5949.72882952009, 4456.931912169165 6122.448979591837, 4648.165410878707 6326.530612244898, 4897.95918367347 6484.284692881059, 5021.544086689852 6530.6122448979595, 5102.040816326531 6558.673625089685, 5306.122448979592 6623.455748266104, 5510.2040816326535 6597.437955895249, 5714.285714285715 6570.203352947625, 5918.367346938776 6543.242785395409, 6122.448979591837 6525.756680235571, 6326.530612244898 6520.453083271883, 6530.6122448979595 6522.261950434471, 6734.693877551021 6533.238936443719, 6938.775510204082 6628.052847726005, 7149.179419692682 6734.693877551021, 7346.938775510204 6858.865387585699, 7447.64756183235 6938.775510204082, 7551.0204081632655 7021.922675930724, 7672.260829380581 7142.857142857143, 7755.102040816327 7225.488935198103, 7876.85861392897 7346.938775510204, 7959.183673469388 7424.887053820552, 8074.276982521525 7551.0204081632655, 8163.265306122449 7660.1472192881065, 8271.702357700893 7755.102040816327, 8367.34693877551 7832.006337691327, 8533.835897640307 7959.183673469388, 8775.510204081633 8142.6900746871015, 8979.591836734695 8375.328219666773, 9183.673469387755 8396.186050103635, 9387.755102040817 8424.58063242387, 9591.836734693878 8459.27180076132, 9795.91836734694 8453.228230379065, 9957.613263811385 8571.428571428572, 10000 8757.661313426739, 10000 8427.640566256101, 9796.219398903246 8371.275719144232, 9383.517404828015 8331.33681649179, 9143.883988913365 8300.273225539891, 8984.1283783036 8184.894173432836, 8771.120897490577 7976.324348470085, 8398.357806067788 7714.50265330408, 8078.846584848256 7359.490185282376, 7683.89521417411 6951.225847057416, 7209.066038195081 6636.152281688155, 6805.239355820393 6449.77073597676, 6294.908933039194 6432.020112575675, 5984.273023520203 6427.582456725404, 5673.6371140012125 6480.834326928666, 5376.314172033036 6489.709638629209, 5145.556067818929 6445.333080126496, 4910.36030775455 6347.704651420527, 4777.230632246412 6223.450287612931, 4542.034872182033 6063.6946770031645, 4324.58973551874 5824.061261088515, 4129.332878106803 5593.303156874407, 3925.2007089943236 5389.170987761928, 3734.3815074326594 5176.163506948902, 3494.7480915180095 5020.8455521894075, 3263.9899873039026 4830.026350627742, 2993.2929804373534 4554.891687910922, 2846.850337378401 4315.258271996272, 2735.908941121619 4088.937823632436, 2780.285499624332 3840.429096017244, 2842.4126815281297 3560.8567774501525, 2944.4787660843695 3361.162264187944, 3082.0460974427792 3294.5974264338747, 3379.369039410956 3170.343062626279, 3845.322903689442 3028.338075417598, 4013.9538259997507 3037.2133871181404, 4320.15207966847 3032.7757312678687, 4542.034872182035 3028.338075417598, 4684.039859390716 2983.9615169148847, 4897.047340203738 2886.333088208916, 5189.932626321643 2766.5163802515917, 5358.563548631952 2673.3256073958946, 5465.067289038463 2611.198425492096, 5744.639607605554 2273.9365808714774, 6246.09471868621 1776.9191256410927, 6641.046089360355 1435.2196251702035, 6822.989979221478 1324.2782289134211, 6978.307933980974 1275.4640145604371, 7311.13212275132 1195.5862092555535, 7444.261798259459 1168.960274153926, 7666.144590773023 1160.0849624533835, 7870.2767598855025 1155.6473066031122, 8052.220649746626 1093.5201246993138, 8331.792968313717 987.0163842928032, 8460.484987971584 920.4515465387335, 8713.43137143705 845.0113970841217, 8855.43635864573 782.8842151803237, 8975.253066603054 671.9428189235414, 9010.754313405225 565.4390785170299, 9046.255560207395 410.1211237575353, 9068.443839458752 281.4291040996677, 9050.693216057667 179.36301954342798, 9006.316657554953 90.60990253800173, 8972.337944103203 0, 8858.95553900271 0, 8979.591836734695 180.16181430038142, 8979.591836734695 360.74278305987923)), ((9935.33621028978 9591.836734693878, 9860.73785898637 9795.91836734694, 9795.91836734694 9931.26849738919, 9765.614100864956 10000, 9959.7366093588 10000, 10000 9899.990932923472, 10000 9210.342095822705, 9950.618354641661 9387.755102040817, 9935.33621028978 9591.836734693878)))',
        'GROUP': 'A',
        'ID': 1,
    },
    {
        'UNITNAME': 'Litho_G',
        'geometry': 'MULTIPOLYGON (((9591.836734693878 7392.409188406808, 9387.755102040817 7366.494159309232, 9183.673469387755 7310.6236360511, 8979.591836734695 7251.495049924267, 8775.510204081633 7185.4665328045285, 8691.716875348773 7142.857142857143, 8571.428571428572 7060.166183783084, 8423.547550123565 6938.775510204082, 8367.34693877551 6891.931806291853, 8163.265306122449 6717.05674151985, 7959.183673469388 6524.418032899195, 7755.102040816327 6316.720222940251, 7530.765922702089 6122.448979591837, 7346.938775510204 5999.901440678811, 7186.986962143256 5918.367346938776, 6938.775510204082 5793.479608029736, 6734.693877551021 5711.484247324418, 6530.6122448979595 5688.577768753987, 6326.530612244898 5674.85692549725, 6122.448979591837 5664.018903459822, 5918.367346938776 5686.95963645468, 5808.41181229572 5714.285714285715, 5714.285714285715 5737.67798287528, 5510.2040816326535 5789.896906638633, 5306.122448979592 5803.500194938816, 5144.4244384765625 5714.285714285715, 4837.004213917013 5510.2040816326535, 4693.877551020409 5412.657990747569, 4564.6032995107225 5306.122448979592, 4489.795918367347 5235.455182133889, 4285.714285714286 4940.409368398238, 4169.117285280811 4693.877551020409, 4290.969225825096 4489.795918367347, 4489.795918367347 4401.180111632056, 4588.951967200454 4285.714285714286, 4693.877551020409 4151.690736108897, 4830.671037946428 3877.5510204081634, 5102.040816326531 3725.3519953513633, 5306.122448979592 3618.5887395119184, 5510.2040816326535 3357.1418450803176, 5714.285714285715 3090.5887058803014, 5921.393024678133 2857.1428571428573, 6122.448979591837 2649.130140032087, 6354.4265591368385 2448.979591836735, 6530.6122448979595 2314.575934896664, 6621.950889120297 2244.8979591836737, 6938.775510204082 2057.7853066580637, 7142.857142857143 1991.364809931541, 7346.938775510204 1953.759679988939, 7551.0204081632655 1939.4851217464525, 7755.102040816327 1938.7210145288584, 7959.183673469388 1951.3825007847379, 8163.265306122449 1964.9159178441885, 8571.428571428572 1920.2366653753788, 8784.97298882932 1836.734693877551, 9174.578141193 1632.6530612244899, 9387.755102040817 1516.645976475307, 9736.033069844148 1224.4897959183675, 10000 887.0183205117985, 10000 0, 8972.337944103203 0, 9006.316657554953 90.60990253800173, 9050.693216057667 179.36301954342798, 9068.443839458752 281.4291040996677, 9046.255560207395 410.1211237575353, 9010.754313405225 565.4390785170299, 8975.253066603054 671.9428189235414, 8855.43635864573 782.8842151803237, 8713.43137143705 845.0113970841217, 8460.484987971584 920.4515465387335, 8331.792968313717 987.0163842928032, 8052.220649746626 1093.5201246993138, 7870.2767598855025 1155.6473066031122, 7666.144590773023 1160.0849624533835, 7444.261798259459 1168.960274153926, 7311.13212275132 1195.5862092555535, 6978.307933980974 1275.4640145604371, 6822.989979221478 1324.2782289134211, 6641.046089360355 1435.2196251702035, 6246.09471868621 1776.9191256410927, 5744.639607605554 2273.9365808714774, 5465.067289038463 2611.198425492096, 5358.563548631952 2673.3256073958946, 5189.932626321643 2766.5163802515917, 4897.047340203738 2886.333088208916, 4684.039859390716 2983.9615169148847, 4542.034872182035 3028.338075417598, 4320.15207966847 3032.7757312678687, 4013.9538259997507 3037.2133871181404, 3845.322903689442 3028.338075417598, 3379.369039410956 3170.343062626279, 3082.0460974427792 3294.5974264338747, 2944.4787660843695 3361.162264187944, 2842.4126815281297 3560.8567774501525, 2780.285499624332 3840.429096017244, 2735.908941121619 4088.937823632436, 2846.850337378401 4315.258271996272, 2993.2929804373534 4554.891687910922, 3263.9899873039026 4830.026350627742, 3494.7480915180095 5020.8455521894075, 3734.3815074326594 5176.163506948902, 3925.2007089943236 5389.170987761928, 4129.332878106803 5593.303156874407, 4324.58973551874 5824.061261088515, 4542.034872182033 6063.6946770031645, 4777.230632246412 6223.450287612931, 4910.36030775455 6347.704651420527, 5145.556067818929 6445.333080126496, 5376.314172033036 6489.709638629209, 5673.6371140012125 6480.834326928666, 5984.273023520203 6427.582456725404, 6294.908933039194 6432.020112575675, 6805.239355820393 6449.77073597676, 7209.066038195081 6636.152281688155, 7683.89521417411 6951.225847057416, 8078.846584848256 7359.490185282376, 8398.357806067788 7714.50265330408, 8771.120897490577 7976.324348470085, 8984.1283783036 8184.894173432836, 9143.883988913365 8300.273225539891, 9383.517404828015 8331.33681649179, 9796.219398903246 8371.275719144232, 10000 8427.640566256101, 10000 7398.084317291527, 9795.91836734694 7385.734246701611, 9591.836734693878 7392.409188406808)), ((10000 10000, 10000 9899.990932923472, 9959.7366093588 10000, 10000 10000)))',
        'GROUP': 'A',
        'ID': 2,
    },
]

for row in geology:
    row['geometry'] = shapely.wkt.loads(row['geometry'])

geology = geopandas.GeoDataFrame(geology, crs='epsg:7854')

# build structures file
structures = [
    {
        'x': 2775.287768202244933,
        'y': 4330.15,
        'strike2': 45.00,
        'dip_2': 45.70,
        'id': 147.00,
        'sf': 's0',
    },
    {
        'x': 3529.794754080061011,
        'y': 3091.192011237949828,
        'strike2': 288.50,
        'dip_2': 41.70,
        'id': 204.00,
        'sf': 's0',
    },
    {
        'x': 7928.315269200518742,
        'y': 7234.561058065713951,
        'strike2': 48.80,
        'dip_2': 41.10,
        'id': 229.00,
        'sf': 's0',
    },
    {
        'x': 8003.966104268994968,
        'y': 7421.634268009857806,
        'strike2': 48.80,
        'dip_2': 41.10,
        'id': 235.00,
        'sf': 's0',
    },
    {
        'x': 6881.165236574942355,
        'y': 1213.128646564158771,
        'strike2': 299.10,
        'dip_2': 44.70,
        'id': 252.00,
        'sf': 's0',
    },
    {
        'x': 3674.015651128655009,
        'y': 5266.677487068354822,
        'strike2': 41.20,
        'dip_2': 40.10,
        'id': 347.00,
        'sf': 's0',
    },
    {
        'x': 3970.895076049027921,
        'y': 2944.223069901633608,
        'strike2': 273.00,
        'dip_2': 46.00,
        'id': 408.00,
        'sf': 's0',
    },
]
for row in structures:
    row['geometry'] = shapely.Point(row['x'], row['y'])
    del row['x'], row['y']

structures = geopandas.GeoDataFrame(structures, crs='epsg:7854')

faults = geopandas.GeoDataFrame(columns=['geometry'], crs='epsg:7854')

f_path = tempfile.mkdtemp()

bounding_box = {"minx": 0, "miny": 0, "maxx": 10000, "maxy": 10000, "base": 0, "top": -5000}

create_raster(
    os.path.join(f_path, "DEM.tif"),
    (bounding_box['minx'], bounding_box['miny'], bounding_box['maxx'], bounding_box['maxy']),
    7854,
    1000,
)

geology.to_file(os.path.join(f_path, "geology.shp"))
structures.to_file(os.path.join(f_path, "structures.shp"))
faults.to_file(os.path.join(f_path, "faults.shp"))
loop_project_filename = os.path.join(f_path, "local_source.loop3d")

config = {
    "structure": {
        "orientation_type": "strike",
        "dipdir_column": "strike2",
        "dip_column": "dip_2",
        "description_column": "DESCRIPTION",
        "bedding_text": "Bed",
        "overturned_column": "structypei",
        "overturned_text": "BEOI",
        "objectid_column": "objectid",
        "desciption_column": "feature",
    },
    "geology": {
        "unitname_column": "UNITNAME",
        "alt_unitname_column": "UNITNAME",
        "group_column": "GROUP",
        "supergroup_column": "supersuite",
        "description_column": "descriptn",
        "minage_column": "min_age_ma",
        "maxage_column": "max_age_ma",
        "rocktype_column": "rocktype1",
        "alt_rocktype_column": "rocktype2",
        "sill_text": "sill",
        "intrusive_text": "intrusive",
        "volcanic_text": "volcanic",
        "objectid_column": "ID",
        "ignore_codes": ["cover"],
    },
    "fault": {
        "structtype_column": "feature",
        "fault_text": "Fault",
        "dip_null_value": "0",
        "dipdir_flag": "num",
        "dipdir_column": "dip_dir",
        "dip_column": "dip",
        "orientation_type": "dip direction",
        "dipestimate_column": "dip_est",
        "dipestimate_text": "gentle,moderate,steep",
        "name_column": "name",
        "objectid_column": "objectid",
    },
    "fold": {
        "structtype_column": "feature",
        "fold_text": "Fold axial trace",
        "description_column": "type",
        "synform_text": "syncline",
        "foldname_column": "NAME",
        "objectid_column": "objectid",
    },
}

module_path = os.path.dirname(map2loop.__file__).replace("__init__.py", "")


@pytest.fixture
def project():
    proj = Project(
        geology_filename=os.path.join(f_path, "geology.shp"),
        fault_filename=os.path.join(f_path, "faults.shp"),
        fold_filename=os.path.join(f_path, "faults.shp"),
        structure_filename=os.path.join(f_path, "structures.shp"),
        dtm_filename=os.path.join(f_path, 'DEM.tif'),
        clut_filename=pathlib.Path(module_path)
        / pathlib.Path('_datasets')
        / pathlib.Path('clut_files')
        / pathlib.Path('WA_clut.csv'),
        config_dictionary=config,
        clut_file_legacy=False,
        working_projection="EPSG:7854",
        bounding_box=bounding_box,
        loop_project_filename=loop_project_filename,
        overwrite_loopprojectfile=True,
    )

    proj.set_thickness_calculator(InterpolatedStructure())

    column = ['Litho_G', 'Litho_F', 'Litho_E']

    proj.set_sampler(Datatype.GEOLOGY, SamplerSpacing(100.0))
    proj.set_sampler(Datatype.STRUCTURE, SamplerDecimator(0))
    proj.run_all(user_defined_stratigraphic_column=column)

    return proj


@pytest.fixture
def interpolated_structure_thickness():
    return InterpolatedStructure()


@pytest.fixture
def units(project):
    return project.stratigraphic_column.stratigraphicUnits


@pytest.fixture
def stratigraphic_order(project):
    return project.stratigraphic_column.column


@pytest.fixture
def basal_contacts(project):
    return project.map_data.basal_contacts


@pytest.fixture
def samples(project):
    return project.structure_samples


@pytest.fixture
def map_data(project):
    return project.map_data


def test_compute(
    interpolated_structure_thickness,
    units,
    stratigraphic_order,
    basal_contacts,
    samples,
    map_data,
    project,
):
    result = interpolated_structure_thickness.compute(
        units, stratigraphic_order, basal_contacts, samples, map_data
    )
    assert (
        interpolated_structure_thickness.thickness_calculator_label == "InterpolatedStructure"
    ), 'Thickness_calc interpolated structure not being set properly'
    assert isinstance(
        result, pd.DataFrame
    ), 'InterpolatedStructure calculator is not returning a DataFrame'
    assert (
        'ThicknessMedian' in result.columns
    ), 'Thickness not being calculated in InterpolatedStructure calculator'
    assert (
        'ThicknessMean' in result.columns
    ), 'Thickness not being calculated in InterpolatedStructure calculator'
    
    assert result['ThicknessMedian'].dtypes is float or int, 'ThicknessMedian column is not float'
    assert (
        'ThicknessStdDev' in result.columns
    ), 'Thickness std not being calculated in InterpolatedStructure calculator'
    assert np.issubdtype(
        result['ThicknessStdDev'].dtypes, np.floating
    ), 'ThicknessStdDev column is not float'

    # check for nas in thickness
    assert result['ThicknessMedian'].isna().sum() == 0, 'ThicknessMedian column has NaNs'
