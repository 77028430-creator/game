"""
Juego de disparos en 2D con Pygame.

Graficos: solo rectangulos y circulos.
- Jugador: cuadrado en la parte inferior, se mueve horizontalmente.
- Disparos: rectangulos que suben al presionar ESPACIO.
- Enemigos: circulos que caen desde arriba.
- Colision disparo-enemigo: el enemigo desaparece y se suman 10 puntos.
- Puntuacion mostrada en la esquina superior izquierda.
Todo contenido en un unico script.
"""

import array
import math
import random
import sys

import pygame

# ---------------------------------------------------------------------------
# Constantes de configuracion
# ---------------------------------------------------------------------------
ANCHO_PANTALLA = 800
ALTO_PANTALLA = 600
FPS = 60

# Colores (RGB)
COLOR_FONDO = (20, 20, 30)
COLOR_JUGADOR = (0, 200, 255)      # Cyan
COLOR_DISPARO = (255, 255, 0)      # Amarillo
COLOR_ENEMIGO = (255, 80, 80)      # Rojo claro
COLOR_TEXTO = (255, 255, 255)      # Blanco

# Medidas y velocidades
TAMANO_JUGADOR = 40
VELOCIDAD_JUGADOR = 7

ANCHO_DISPARO = 6
ALTO_DISPARO = 15
VELOCIDAD_DISPARO = 9

RADIO_ENEMIGO = 20
VELOCIDAD_ENEMIGO_MIN = 2
VELOCIDAD_ENEMIGO_MAX = 5
TASA_APARICION_ENEMIGO = 30  # frames entre apariciones (menor = mas frecuente)

PUNTOS_POR_ENEMIGO = 10

# ---------------------------------------------------------------------------
# Configuracion de audio (sonidos generados sinteticamente)
# ---------------------------------------------------------------------------
FRECUENCIA_MUESTRA = 44100   # Hz
CANNALES_AUDIO = -1          # -1 = estereo, 1 = mono, 2 = estereo
BITS_POR_MUESTRA = -16       # 16 bits con signo
TAMAÑO_BUFFER = 512

# Volumen de los efectos (0.0 a 1.0)
VOLUMEN_DISPARO = 0.4
VOLUMEN_COLISION = 0.5
VOLUMEN_GAME_OVER = 0.6


# ---------------------------------------------------------------------------
# Clases del juego
# ---------------------------------------------------------------------------
class Jugador:
    """Cuadrado controlado por el usuario en la parte inferior de la pantalla."""

    def __init__(self):
        self.ancho = TAMANO_JUGADOR
        self.alto = TAMANO_JUGADOR
        self.x = ANCHO_PANTALLA // 2 - self.ancho // 2
        self.y = ALTO_PANTALLA - self.alto - 20
        self.velocidad = VELOCIDAD_JUGADOR

    def mover(self, direccion):
        """Mueve al jugador horizontalmente (-1 izquierda, 1 derecha, 0 quieto)."""
        self.x += direccion * self.velocidad
        # Limitar a los bordes de la pantalla
        if self.x < 0:
            self.x = 0
        if self.x + self.ancho > ANCHO_PANTALLA:
            self.x = ANCHO_PANTALLA - self.ancho

    def dibujar(self, superficie):
        pygame.draw.rect(
            superficie,
            COLOR_JUGADOR,
            (self.x, self.y, self.ancho, self.alto),
            border_radius=4,
        )

    def obtener_rect(self):
        return pygame.Rect(self.x, self.y, self.ancho, self.alto)


class Disparo:
    """Rectangulo que se desplaza hacia arriba."""

    def __init__(self, x, y):
        self.ancho = ANCHO_DISPARO
        self.alto = ALTO_DISPARO
        # Centrar el disparo en la parte superior del jugador
        self.x = x + TAMANO_JUGADOR // 2 - self.ancho // 2
        self.y = y - ALTO_DISPARO
        self.velocidad = VELOCIDAD_DISPARO
        self.activo = True

    def actualizar(self):
        self.y -= self.velocidad
        if self.y + self.alto < 0:
            self.activo = False

    def dibujar(self, superficie):
        pygame.draw.rect(superficie, COLOR_DISPARO, (self.x, self.y, self.ancho, self.alto))

    def obtener_rect(self):
        return pygame.Rect(self.x, self.y, self.ancho, self.alto)


class Enemigo:
    """Circulo que cae desde la parte superior de la pantalla."""

    def __init__(self):
        self.radio = RADIO_ENEMIGO
        self.x = random.randint(self.radio, ANCHO_PANTALLA - self.radio)
        self.y = -self.radio
        self.velocidad = random.uniform(VELOCIDAD_ENEMIGO_MIN, VELOCIDAD_ENEMIGO_MAX)
        self.activo = True

    def actualizar(self):
        self.y += self.velocidad
        if self.y - self.radio > ALTO_PANTALLA:
            self.activo = False

    def dibujar(self, superficie):
        pygame.draw.circle(superficie, COLOR_ENEMIGO, (int(self.x), int(self.y)), self.radio)

    def obtener_rect(self):
        # Rectangulo envolvente para colisiones (aproximacion del circulo)
        return pygame.Rect(
            self.x - self.radio,
            self.y - self.radio,
            self.radio * 2,
            self.radio * 2,
        )


class GestorSonidos:
    """Genera y reproduce efectos de sonido sinteticos sin archivos externos."""

    def __init__(self):
        self.habilitado = False
        try:
            pygame.mixer.init(
                frequency=FRECUENCIA_MUESTRA,
                size=-BITS_POR_MUESTRA if BITS_POR_MUESTRA < 0 else BITS_POR_MUESTRA,
                channels=CANNALES_AUDIO if CANNALES_AUDIO > 0 else 2,
                buffer=TAMAÑO_BUFFER,
            )
            self.habilitado = True
        except pygame.error:
            # Si no hay dispositivo de audio, continuamos sin sonido
            self.habilitado = False

        self.sonido_disparo = self._crear_sonido_disparo()
        self.sonido_colision = self._crear_sonido_colision()
        self.sonido_game_over = self._crear_sonido_game_over()

    def _generar_tono(self, frecuencia, duracion, volumen=0.5, tipo="seno"):
        """Genera un buffer de audio para un tono simple."""
        if not self.habilitado:
            return None

        num_muestras = int(FRECUENCIA_MUESTRA * duracion)
        buffer = array.array("h")  # 'h' = signed short (16 bits)

        for i in range(num_muestras):
            t = i / FRECUENCIA_MUESTRA
            if tipo == "seno":
                muestra = math.sin(2 * math.pi * frecuencia * t)
            elif tipo == "cuadrado":
                muestra = 1.0 if math.sin(2 * math.pi * frecuencia * t) >= 0 else -1.0
            elif tipo == "diente":
                muestra = 2 * (t * frecuencia - math.floor(t * frecuencia + 0.5))
            elif tipo == "ruido":
                muestra = random.uniform(-1.0, 1.0)
            else:
                muestra = 0.0

            # Aplicar envolvente simple para evitar clics
            ataque = 0.01
            liberacion = 0.05
            if t < ataque:
                muestra *= t / ataque
            elif t > duracion - liberacion:
                muestra *= (duracion - t) / liberacion

            valor = int(muestra * volumen * 32767)
            buffer.append(valor)
            if CANNALES_AUDIO == -1 or CANNALES_AUDIO == 2:
                buffer.append(valor)  # mismo valor para ambos canales

        return pygame.mixer.Sound(buffer=buffer)

    def _crear_sonido_disparo(self):
        """Beep agudo y corto para el disparo."""
        sonido = self._generar_tono(
            frecuencia=880, duracion=0.12, volumen=VOLUMEN_DISPARO, tipo="seno"
        )
        if sonido:
            sonido.set_volume(VOLUMEN_DISPARO)
        return sonido

    def _crear_sonido_colision(self):
        """Tono descendente para cuando un disparo impacta un enemigo."""
        sonido = self._generar_tono(
            frecuencia=440, duracion=0.18, volumen=VOLUMEN_COLISION, tipo="diente"
        )
        if sonido:
            sonido.set_volume(VOLUMEN_COLISION)
        return sonido

    def _crear_sonido_game_over(self):
        """Tono grave y prolongado para Game Over."""
        sonido = self._generar_tono(
            frecuencia=150, duracion=0.8, volumen=VOLUMEN_GAME_OVER, tipo="seno"
        )
        if sonido:
            sonido.set_volume(VOLUMEN_GAME_OVER)
        return sonido

    def reproducir_disparo(self):
        if self.habilitado and self.sonido_disparo:
            self.sonido_disparo.play()

    def reproducir_colision(self):
        if self.habilitado and self.sonido_colision:
            self.sonido_colision.play()

    def reproducir_game_over(self):
        if self.habilitado and self.sonido_game_over:
            self.sonido_game_over.play()


# ---------------------------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------------------------
def verificar_colision(rect1, rect2):
    """Devuelve True si dos rectangulos se solapan."""
    return rect1.colliderect(rect2)


def colision_circulo_rect(circulo_x, circulo_y, radio, rect):
    """Comprueba colision precisa entre un circulo y un rectangulo."""
    # Punto mas cercano en el rectangulo al centro del circulo
    punto_x = max(rect.left, min(circulo_x, rect.right))
    punto_y = max(rect.top, min(circulo_y, rect.bottom))

    dx = circulo_x - punto_x
    dy = circulo_y - punto_y

    return dx * dx + dy * dy <= radio * radio


# ---------------------------------------------------------------------------
# Bucle principal del juego
# ---------------------------------------------------------------------------
def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
    pygame.display.set_caption("Juego de Disparos 2D - Pygame")
    reloj = pygame.time.Clock()
    fuente = pygame.font.SysFont(None, 36)
    sonidos = GestorSonidos()

    jugador = Jugador()
    disparos = []
    enemigos = []
    puntuacion = 0
    contador_aparicion = 0
    juego_activo = True

    while True:
        # --- Eventos ---
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if juego_activo and evento.key == pygame.K_SPACE:
                    disparos.append(Disparo(jugador.x, jugador.y))
                    sonidos.reproducir_disparo()
                if not juego_activo and evento.key == pygame.K_r:
                    # Reiniciar partida
                    jugador = Jugador()
                    disparos = []
                    enemigos = []
                    puntuacion = 0
                    contador_aparicion = 0
                    juego_activo = True

        if juego_activo:
            # --- Movimiento del jugador ---
            teclas = pygame.key.get_pressed()
            direccion = 0
            if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
                direccion = -1
            if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
                direccion = 1
            jugador.mover(direccion)

            # --- Disparos ---
            for disparo in disparos:
                disparo.actualizar()
            disparos = [d for d in disparos if d.activo]

            # --- Enemigos ---
            contador_aparicion += 1
            if contador_aparicion >= TASA_APARICION_ENEMIGO:
                enemigos.append(Enemigo())
                contador_aparicion = 0
                # Hacer ligeramente mas frecuente la aparicion con el tiempo
                if TASA_APARICION_ENEMIGO > 15:
                    pass  # se mantiene constante para simplicidad

            for enemigo in enemigos:
                enemigo.actualizar()
            enemigos = [e for e in enemigos if e.activo]

            # --- Colisiones disparo vs enemigo ---
            for disparo in disparos:
                if not disparo.activo:
                    continue
                rect_disparo = disparo.obtener_rect()
                for enemigo in enemigos:
                    if not enemigo.activo:
                        continue
                    # Colision preciso circulo-rectangulo
                    if colision_circulo_rect(
                        enemigo.x, enemigo.y, enemigo.radio, rect_disparo
                    ):
                        disparo.activo = False
                        enemigo.activo = False
                        puntuacion += PUNTOS_POR_ENEMIGO
                        sonidos.reproducir_colision()
                        break

            # --- Colision enemigo vs jugador (fin de juego) ---
            rect_jugador = jugador.obtener_rect()
            for enemigo in enemigos:
                if colision_circulo_rect(
                    enemigo.x, enemigo.y, enemigo.radio, rect_jugador
                ):
                    juego_activo = False
                    sonidos.reproducir_game_over()
                    break

        # --- Dibujo ---
        pantalla.fill(COLOR_FONDO)

        jugador.dibujar(pantalla)

        for disparo in disparos:
            disparo.dibujar(pantalla)

        for enemigo in enemigos:
            enemigo.dibujar(pantalla)

        # Puntuacion en esquina superior izquierda
        texto_puntuacion = fuente.render(f"Puntuacion: {puntuacion}", True, COLOR_TEXTO)
        pantalla.blit(texto_puntuacion, (10, 10))

        if not juego_activo:
            texto_game_over = fuente.render(
                "GAME OVER - Presiona R para reiniciar", True, COLOR_TEXTO
            )
            rect_texto = texto_game_over.get_rect(
                center=(ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2)
            )
            pantalla.blit(texto_game_over, rect_texto)

        pygame.display.flip()
        reloj.tick(FPS)


if __name__ == "__main__":
    main()
