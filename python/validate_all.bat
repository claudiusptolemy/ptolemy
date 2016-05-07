python validate.py --model triangulate --xlsx D:\repos\ptolemy\input\ArabiaDeserta.xlsx --output D:\repos\ptolemy\output\validate_triangulate_ArabiaDeserta.csv --prior arabia_prior.png --lower_left_lon 30 --lower_left_lat 10 --upper_right_lon 60 --upper_right_lat 40
python validate.py --model triangulate --xlsx D:\repos\ptolemy\input\ArabiaFelix.xlsx --output D:\repos\ptolemy\output\validate_triangulate_ArabiaFelix.csv --prior arabia_prior.png --lower_left_lon 30 --lower_left_lat 10 --upper_right_lon 60 --upper_right_lat 40
python validate.py --model triangulate --xlsx D:\repos\ptolemy\input\ArabiaPetraea.xlsx --output D:\repos\ptolemy\output\validate_triangulate_ArabiaPetraea.csv --prior arabia_prior.png --lower_left_lon 30 --lower_left_lat 10 --upper_right_lon 60 --upper_right_lat 40
python validate.py --model triangulate --xlsx D:\repos\ptolemy\input\JudaeaPalestina.xlsx --output D:\repos\ptolemy\output\validate_triangulate_JudaeaPalestina.csv --prior arabia_prior.png --lower_left_lon 30 --lower_left_lat 10 --upper_right_lon 60 --upper_right_lat 40
python validate.py --model triangulate --xlsx D:\repos\ptolemy\input\Syria.xlsx --output D:\repos\ptolemy\output\validate_triangulate_Syria.csv --prior arabia_prior.png --lower_left_lon 30 --lower_left_lat 10 --upper_right_lon 60 --upper_right_lat 40
python plot_validation.py --input D:\repos\ptolemy\output\validate_triangulate_ArabiaDeserta.csv
python plot_validation.py --input D:\repos\ptolemy\output\validate_triangulate_ArabiaFelix.csv
python plot_validation.py --input D:\repos\ptolemy\output\validate_triangulate_ArabiaPetraea.csv
python plot_validation.py --input D:\repos\ptolemy\output\validate_triangulate_JudaeaPalestina.csv
python plot_validation.py --input D:\repos\ptolemy\output\validate_triangulate_Syria.csv
python validate.py --model flocking --xlsx D:\repos\ptolemy\input\ArabiaDeserta.xlsx --output D:\repos\ptolemy\output\validate_flocking_ArabiaDeserta.csv --prior arabia_prior.png --lower_left_lon 30 --lower_left_lat 10 --upper_right_lon 60 --upper_right_lat 40
python validate.py --model flocking --xlsx D:\repos\ptolemy\input\ArabiaFelix.xlsx --output D:\repos\ptolemy\output\validate_flocking_ArabiaFelix.csv --prior arabia_prior.png --lower_left_lon 30 --lower_left_lat 10 --upper_right_lon 60 --upper_right_lat 40
python validate.py --model flocking --xlsx D:\repos\ptolemy\input\ArabiaPetraea.xlsx --output D:\repos\ptolemy\output\validate_flocking_ArabiaPetraea.csv --prior arabia_prior.png --lower_left_lon 30 --lower_left_lat 10 --upper_right_lon 60 --upper_right_lat 40
python validate.py --model flocking --xlsx D:\repos\ptolemy\input\JudaeaPalestina.xlsx --output D:\repos\ptolemy\output\validate_flocking_JudaeaPalestina.csv --prior arabia_prior.png --lower_left_lon 30 --lower_left_lat 10 --upper_right_lon 60 --upper_right_lat 40
python validate.py --model flocking --xlsx D:\repos\ptolemy\input\Syria.xlsx --output D:\repos\ptolemy\output\validate_flocking_Syria.csv --prior arabia_prior.png --lower_left_lon 30 --lower_left_lat 10 --upper_right_lon 60 --upper_right_lat 40
python plot_validation.py --input D:\repos\ptolemy\output\validate_flocking_ArabiaDeserta.csv
python plot_validation.py --input D:\repos\ptolemy\output\validate_flocking_ArabiaFelix.csv
python plot_validation.py --input D:\repos\ptolemy\output\validate_flocking_ArabiaPetraea.csv
python plot_validation.py --input D:\repos\ptolemy\output\validate_flocking_JudaeaPalestina.csv
python plot_validation.py --input D:\repos\ptolemy\output\validate_flocking_Syria.csv
python validate.py --model triangulate --sgdb 7.01 --output D:\repos\ptolemy\output\validate_triangulate_India.csv --prior prior_India.png --lower_left_lon 65 --lower_left_lat 5 --upper_right_lon 95 --upper_right_lat 35
python validate.py --model flocking --sgdb 7.01 --output D:\repos\ptolemy\output\validate_flocking_India.csv --prior prior_India.png --lower_left_lon 65 --lower_left_lat 5 --upper_right_lon 95 --upper_right_lat 35
python validate.py --model triangulate --sgdb 7.04 --output D:\repos\ptolemy\output\validate_triangulate_Taprobane.csv --prior prior_Taprobane.png --lower_left_lon 78 --lower_left_lat 5 --upper_right_lon 83 --upper_right_lat 10
python validate.py --model flocking --sgdb 7.04 --output D:\repos\ptolemy\output\validate_flocking_Taprobane.csv --prior prior_Taprobane.png --lower_left_lon 78 --lower_left_lat 5 --upper_right_lon 83 --upper_right_lat 10
python plot_validation.py --input D:\repos\ptolemy\output\validate_triangulate_India.csv
python plot_validation.py --input D:\repos\ptolemy\output\validate_flocking_India.csv
python plot_validation.py --input D:\repos\ptolemy\output\validate_triangulate_Taprobane.csv
python plot_validation.py --input D:\repos\ptolemy\output\validate_flocking_Taprobane.csv
