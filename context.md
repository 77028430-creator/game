# Contexto del Proyecto - Juego de Disparos 2D

## Estado actual
✅ Proyecto inicial completado y funcionando.

## Descripción
Juego de disparos en 2D desarrollado en Python utilizando Pygame (pygame-ce).
Todos los gráficos están hechos con figuras geométricas simples (rectángulos y círculos).
Todo el juego está contenido en un único script.

## Archivos del proyecto
- `juego_disparos.py` — Script principal del juego (único archivo).
- `context.md` — Este archivo de contexto y avances.

## Tecnologías
- Lenguaje: Python 3.14.2
- Librería: pygame-ce 2.5.8 (fork activo de pygame, se importa como `pygame`)
- Sistema operativo: Windows (win32)

## Funcionalidades implementadas
- Jugador: cuadrado cyan en la parte inferior, movimiento horizontal (← → / A D).
- Disparos: rectángulos amarillos que suben al presionar ESPACIO.
- Enemigos: círculos rojos que caen desde la parte superior.
- **Sonido: efectos generados sinteticamente (sin archivos externos):**
  - Disparo: beep agudo y corto.
  - Colisión disparo-enemigo: tono descendente.
  - Game Over: tono grave prolongado.
- Colisiones:
  - Disparo + enemigo → enemigo eliminado, +10 puntos.
  - Enemigo + jugador → Game Over.
- Puntuación mostrada en la esquina superior izquierda.
- Pantalla de Game Over con opción de reiniciar (tecla R).
- Límite de pantalla para el jugador (no sale de los bordes).
- Disparos y enemigos se eliminan al salir de la pantalla.

## Controles
- ← → o A D: mover jugador
- ESPACIO: disparar
- R: reiniciar partida (tras Game Over)
- ESC: salir del juego

## Cómo ejecutar
```powershell
cd "C:\Users\LAB05-SJL\Documents\Proyecto predeterminado"
python juego_disparos.py
```

## Próximos pasos / cambios pendientes
- (Ninguno definido aún. Agregar aquí nuevas funcionalidades o mejoras a medida que se avancen.)

## Historial de cambios
- v1.0.0 — Creación inicial del juego con mecánicas básicas de disparo, enemigos, puntuación y Game Over.
- v1.1.0 — Agregado sistema de sonido sintético: efectos de disparo, colisión y Game Over generados proceduralmente sin archivos de audio externos.