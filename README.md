# R1-Conteo-Personas
En un parque se desea detectar y contar la cantidad de personas que cruzan cierta parte del parque. Durante el dia se graba un video para luego procesarlo y obtener la cantidad de personas que cruzaron una linea virtual (horizontal) en el video. Se desea que cada persona se cuente una sola vez, aunque cruce la línea varias veces.


### ¿Cómo correrlo ahora?

**1. Clonar o preparar el directorio**
```bash
git clone https://github.com/BryanEstrada003/R1-Conteo-Personas.git
```

**2. Crear un entorno virtual (Recomendado) e instalas las librerías**
```bash
python3 -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate}
pip install -r requirements.txt
```

Si tu video está en la misma carpeta:

```bash
python3 conteo.py video_parque.mp4
```

Si el video está en otra carpeta, le pasas la ruta completa o relativa:

```bash
python3 conteo.py /ruta/a/tu/carpeta/video_parque.mp4

```
