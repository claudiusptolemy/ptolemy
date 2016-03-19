python validate.py --model triangulate --xlsx D:\repos\ptolemy\input\ArabiaDeserta.xlsx --output C:\Users\Corey\Desktop\validate_ArabiaDeserta.csv
python validate.py --model triangulate --xlsx D:\repos\ptolemy\input\ArabiaFelix.xlsx --output C:\Users\Corey\Desktop\validate_ArabiaFelix.csv
python validate.py --model triangulate --xlsx D:\repos\ptolemy\input\ArabiaPetraea.xlsx --output C:\Users\Corey\Desktop\validate_ArabiaPetraea.csv
python validate.py --model triangulate --xlsx D:\repos\ptolemy\input\JudaeaPalestina.xlsx --output C:\Users\Corey\Desktop\validate_JudaeaPalestina.csv
python validate.py --model triangulate --xlsx D:\repos\ptolemy\input\Syria.xlsx --output C:\Users\Corey\Desktop\validate_Syria.csv
python plot_validation.py --input C:\Users\Corey\Desktop\validate_ArabiaDeserta.csv
python plot_validation.py --input C:\Users\Corey\Desktop\validate_ArabiaFelix.csv
python plot_validation.py --input C:\Users\Corey\Desktop\validate_ArabiaPetraea.csv
python plot_validation.py --input C:\Users\Corey\Desktop\validate_JudaeaPalestina.csv
python plot_validation.py --input C:\Users\Corey\Desktop\validate_Syria.csv