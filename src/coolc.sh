# Incluya aquí las instrucciones necesarias para ejecutar su compilador

INPUT_FILE=$1
OUTPUT_FILE=${INPUT_FILE:0: -2}mips

python3 main.py $INPUT_FILE $OUTPUT_FILE

# Si su compilador no lo hace ya, aquí puede imprimir la información de contacto
echo "coolc v1.0"   # Recuerde cambiar estas
echo "Copyright (c) 2019: Alexander A. Gonzalez Fertel, Leonardo Fleitas, Marcos Toranzo"    # líneas a los valores correctos

# Llamar al compilador
# echo "Compiling $INPUT_FILE into $OUTPUT_FILE"

