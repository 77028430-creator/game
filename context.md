# Contexto del Proyecto - Juego de Disparos 2D

## Estado actual
✅ Proyecto en modo multijugador (2 jugadores) y funcionando.

## Descripción
Juego de disparos en 2D para 2 jugadores desarrollado en Python utilizando Pygame (pygame-ce).
Todos los gráficos están hechos con figuras geométricas simples (rectángulos y círculos).
Todo el juego está contenido en un único script.

## Archivos del proyecto
- `juego_disparos.py` — Script principal del juego (único archivo).
- `context.md` — Este archivo de contexto y avances.
- `.gitignore` — Archivos excluidos del control de versiones.

## Tecnologías
- Lenguaje: Python 3.14.2
- Librería: pygame-ce 2.5.8 (fork activo de pygame, se importa como `pygame`)
- Sistema operativo: Windows (win32)

## Funcionalidades implementadas
- Jugador 1: cuadrado cyan en la parte inferior izquierda, se mueve con A/D, dispara con ESPACIO.
- Jugador 2: cuadrado magenta en la parte inferior derecha, se mueve con flechas izquierda/derecha, dispara con SHIFT derecho.
- Disparos: rectangulos de colores (amarillo para P1, cyan claro para P2) que suben al presionar la tecla de disparo.
- Enemigos: circulos rojos que caen desde la parte superior.
- **Sonido: efectos generados sinteticamente (sin archivos externos):**
  - Disparo P1: beep agudo (880 Hz).
  - Disparo P2: beep medio (660 Hz).
  - Colisión disparo-enemigo: tono descendente.
  - Game Over: tono grave prolongado.
- Colisiones:
  - Disparo + enemigo -> enemigo eliminado, el jugador que disparo suma +10 puntos.
  - Enemigo + cualquier jugador -> Game Over.
- Puntuacion individual de cada jugador mostrada en la parte superior (izquierda y derecha).
- Pantalla de Game Over con opcion de reiniciar (tecla R).
- Limite de pantalla para ambos jugadores (no salen de los bordes).
- Disparos y enemigos se eliminan al salir de la pantalla.
- Indicador de controles en la parte inferior de la pantalla.

## Controles
| Jugador | Mover izquierda | Mover derecha | Disparar |
|---------|-----------------|---------------|----------|
| Jugador 1 | A | D | ESPACIO |
| Jugador 2 | Flecha Izq | Flecha Der | SHIFT Derecho |
| Ambos | - | - | R (reiniciar tras Game Over) |
| Ambos | - | - | ESC (salir) |

## Cómo ejecutar
```powershell
cd "C:\Users\LAB05-SJL\Documents\Proyecto predeterminado"
python juego_disparos.py
```

## Próximos pasos / cambios pendientes
- (Ninguno definido aún. Agregar aquí nuevas funcionalidades o mejoras a medida que se avancen.)

## Historial de cambios
- v1.0.0 — Creación inicial del juego para 1 jugador con mecánicas básicas de disparo, enemigos, puntuación y Game Over.
- v1.1.0 — Agregado sistema de sonido sintético: efectos de disparo, colisión y Game Over generados proceduralmente sin archivos de audio externos.
- v2.0.0 — Convertido a multijugador de 2 jugadores: dos cuadrados independientes, controles separados, puntuaciones individuales y sonidos diferenciados por jugador.