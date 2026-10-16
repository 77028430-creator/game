"""
Juego de disparos en 2D para 2 jugadores con Pygame.

Graficos: solo rectangulos y circulos.
- Dos jugadores: cuadrados en la parte inferior, se mueven horizontalmente.
- Disparos: rectangulos que suben al presionar la tecla de disparo de cada jugador.
- Enemigos: circulos que caen desde la parte superior.
- Colision disparo-enemigo: el enemigo desaparece y el jugador que disparo suma puntos.
- Puntuacion individual de cada jugador mostrada en la parte superior.
- Game Over si un enemigo toca a cualquiera de los dos jugadores.
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
COLOR_JUGADOR_1 = (0, 200, 255)     # Cyan
COLOR_JUGADOR_2 = (255, 0, 255)     # Magenta
COLOR_DISPARO_1 = (255, 255, 0)     # Amarillo
COLOR_DISPARO_2 = (0, 255, 255)     # Cyan claro
COLOR_ENEMIGO = (255, 80, 80)       # Rojo claro
COLOR_TEXTO = (255, 255, 255)       # Blanco

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

# Posiciones iniciales de los jugadores
JUGADOR_1_X = 100
JUGADOR_2_X = ANCHO_PANTALLA - 100 - TAMANO_JUGADOR
Y_JUGADORES = ALTO_PANTALLA - TAMANO_JUGADOR - 20


# ---------------------------------------------------------------------------
# Configuracion de audio (sonidos generados sinteticamente)
# ---------------------------------------------------------------------------
FRECUENCIA_MUESTRA = 44100   # Hz
BITS_POR_MUESTRA = 16        # 16 bits con signo
TAMAÑO_BUFFER = 512

# Volumen de los efectos (0.0 a 1.0)
VOLUMEN_DISPARO = 0.4
VOLUMEN_COLISION = 0.5
VOLUMEN_GAME_OVER = 0.6


# ---------------------------------------------------------------------------
# Clases del juego
# ---------------------------------------------------------------------------
class Jugador:
    """Cuadrado controlado por un usuario en la parte inferior de la pantalla."""

    def __init__(self, numero, x, color, tecla_izq, tecla_der, tecla_disparo):
        self.numero = numero
        self.ancho = TAMANO_JUGADOR
        self.alto = TAMANO_JUGADOR
        self.x = x
        self.y = Y_JUGADORES
        self.color = color
        self.velocidad = VELOCIDAD_JUGADOR
        self.tecla_izq = tecla_izq
        self.tecla_der = tecla_der
        self.tecla_disparo = tecla_disparo
        self.puntuacion = 0

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
            self.color,
            (self.x, self.y, self.ancho, self.alto),
            border_radius=4,
        )

    def obtener_rect(self):
        return pygame.Rect(self.x, self.y, self.ancho, self.alto)


class Disparo:
    """Rectangulo que se desplaza hacia arriba disparado por un jugador."""

    def __init__(self, x, y, color):
        self.ancho = ANCHO_DISPARO
        self.alto = ALTO_DISPARO
        # Centrar el disparo en la parte superior del jugador
        self.x = x + TAMANO_JUGADOR // 2 - self.ancho // 2
        self.y = y - ALTO_DISPARO
        self.color = color
        self.velocidad = VELOCIDAD_DISPARO
        self.activo = True

    def actualizar(self):
        self.y -= self.velocidad
        if self.y + self.alto < 0:
            self.activo = False

    def dibujar(self, superficie):
        pygame.draw.rect(superficie, self.color, (self.x, self.y, self.ancho, self.alto))

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
                size=-BITS_POR_MUESTRA,
                channels=2,
                buffer=TAMAÑO_BUFFER,
            )
            self.habilitado = True
        except pygame.error:
            self.habilitado = False

        self.sonido_disparo_1 = self._crear_sonido_disparo(880, VOLUMEN_DISPARO)
        self.sonido_disparo_2 = self._crear_sonido_disparo(660, VOLUMEN_DISPARO)
        self.sonido_colision = self._crear_sonido_colision()
        self.sonido_game_over = self._crear_sonido_game_over()

    def _generar_tono(self, frecuencia, duracion, volumen=0.5, tipo="seno"):
        """Genera un buffer de audio para un tono simple."""
        if not self.habilitado:
            return None

        num_muestras = int(FRECUENCIA_MUESTRA * duracion)
        buffer = array.array("h")  # signed short (16 bits)

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

            # Envolvente simple para evitar clics
            ataque = 0.01
            liberacion = 0.05
            if t < ataque:
                muestra *= t / ataque
            elif t > duracion - liberacion:
                muestra *= (duracion - t) / liberacion

            valor = int(muestra * volumen * 32767)
            buffer.append(valor)
            buffer.append(valor)  # estereo: mismo valor para ambos canales

        return pygame.mixer.Sound(buffer=buffer)

    def _crear_sonido_disparo(self, frecuencia, volumen):
        sonido = self._generar_tono(
            frecuencia=frecuencia, duracion=0.12, volumen=volumen, tipo="seno"
        )
        if sonido:
            sonido.set_volume(volumen)
        return sonido

    def _crear_sonido_colision(self):
        sonido = self._generar_tono(
            frecuencia=440, duracion=0.18, volumen=VOLUMEN_COLISION, tipo="diente"
        )
        if sonido:
            sonido.set_volume(VOLUMEN_COLISION)
        return sonido

    def _crear_sonido_game_over(self):
        sonido = self._generar_tono(
            frecuencia=150, duracion=0.8, volumen=VOLUMEN_GAME_OVER, tipo="seno"
        )
        if sonido:
            sonido.set_volume(VOLUMEN_GAME_OVER)
        return sonido

    def reproducir_disparo(self, numero_jugador):
        if not self.habilitado:
            return
        if numero_jugador == 1 and self.sonido_disparo_1:
            self.sonido_disparo_1.play()
        elif numero_jugador == 2 and self.sonido_disparo_2:
            self.sonido_disparo_2.play()

    def reproducir_colision(self):
        if self.habilitado and self.sonido_colision:
            self.sonido_colision.play()

    def reproducir_game_over(self):
        if self.habilitado and self.sonido_game_over:
            self.sonido_game_over.play()


# ---------------------------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------------------------
def colision_circulo_rect(circulo_x, circulo_y, radio, rect):
    """Comprueba colision precisa entre un circulo y un rectangulo."""
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
    pygame.display.set_caption("Juego de Disparos 2D - 2 Jugadores")
    reloj = pygame.time.Clock()
    fuente = pygame.font.SysFont(None, 36)
    fuente_pequena = pygame.font.SysFont(None, 28)
    sonidos = GestorSonidos()

    # Crear dos jugadores
    jugador_1 = Jugador(
        numero=1,
        x=JUGADOR_1_X,
        color=COLOR_JUGADOR_1,
        tecla_izq=pygame.K_a,
        tecla_der=pygame.K_d,
        tecla_disparo=pygame.K_SPACE,
    )
    jugador_2 = Jugador(
        numero=2,
        x=JUGADOR_2_X,
        color=COLOR_JUGADOR_2,
        tecla_izq=pygame.K_LEFT,
        tecla_der=pygame.K_RIGHT,
        tecla_disparo=pygame.K_RSHIFT,
    )

    disparos = []
    enemigos = []
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
                if juego_activo:
                    if evento.key == jugador_1.tecla_disparo:
                        disparos.append(Disparo(jugador_1.x, jugador_1.y, COLOR_DISPARO_1))
                        sonidos.reproducir_disparo(1)
                    if evento.key == jugador_2.tecla_disparo:
                        disparos.append(Disparo(jugador_2.x, jugador_2.y, COLOR_DISPARO_2))
                        sonidos.reproducir_disparo(2)
                if not juego_activo and evento.key == pygame.K_r:
                    # Reiniciar partida
                    jugador_1 = Jugador(
                        numero=1,
                        x=JUGADOR_1_X,
                        color=COLOR_JUGADOR_1,
                        tecla_izq=pygame.K_a,
                        tecla_der=pygame.K_d,
                        tecla_disparo=pygame.K_SPACE,
                    )
                    jugador_2 = Jugador(
                        numero=2,
                        x=JUGADOR_2_X,
                        color=COLOR_JUGADOR_2,
                        tecla_izq=pygame.K_LEFT,
                        tecla_der=pygame.K_RIGHT,
                        tecla_disparo=pygame.K_RSHIFT,
                    )
                    disparos = []
                    enemigos = []
                    contador_aparicion = 0
                    juego_activo = True

        if juego_activo:
            # --- Movimiento de los jugadores ---
            teclas = pygame.key.get_pressed()

            direccion_1 = 0
            if teclas[jugador_1.tecla_izq]:
                direccion_1 = -1
            if teclas[jugador_1.tecla_der]:
                direccion_1 = 1
            jugador_1.mover(direccion_1)

            direccion_2 = 0
            if teclas[jugador_2.tecla_izq]:
                direccion_2 = -1
            if teclas[jugador_2.tecla_der]:
                direccion_2 = 1
            jugador_2.mover(direccion_2)

            # --- Disparos ---
            for disparo in disparos:
                disparo.actualizar()
            disparos = [d for d in disparos if d.activo]

            # --- Enemigos ---
            contador_aparicion += 1
            if contador_aparicion >= TASA_APARICION_ENEMIGO:
                enemigos.append(Enemigo())
                contador_aparicion = 0

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
                    if colision_circulo_rect(
                        enemigo.x, enemigo.y, enemigo.radio, rect_disparo
                    ):
                        disparo.activo = False
                        enemigo.activo = False
                        # Asignar puntos segun el color del disparo
                        if disparo.color == COLOR_DISPARO_1:
                            jugador_1.puntuacion += PUNTOS_POR_ENEMIGO
                        else:
                            jugador_2.puntuacion += PUNTOS_POR_ENEMIGO
                        sonidos.reproducir_colision()
                        break

            # --- Colision enemigo vs cualquiera de los jugadores (fin de juego) ---
            rect_jugador_1 = jugador_1.obtener_rect()
            rect_jugador_2 = jugador_2.obtener_rect()
            for enemigo in enemigos:
                if colision_circulo_rect(
                    enemigo.x, enemigo.y, enemigo.radio, rect_jugador_1
                ) or colision_circulo_rect(
                    enemigo.x, enemigo.y, enemigo.radio, rect_jugador_2
                ):
                    juego_activo = False
                    sonidos.reproducir_game_over()
                    break

        # --- Dibujo ---
        pantalla.fill(COLOR_FONDO)

        jugador_1.dibujar(pantalla)
        jugador_2.dibujar(pantalla)

        for disparo in disparos:
            disparo.dibujar(pantalla)

        for enemigo in enemigos:
            enemigo.dibujar(pantalla)

        # Puntuaciones en la parte superior
        texto_p1 = fuente.render(f"Jugador 1: {jugador_1.puntuacion}", True, COLOR_JUGADOR_1)
        texto_p2 = fuente.render(f"Jugador 2: {jugador_2.puntuacion}", True, COLOR_JUGADOR_2)
        pantalla.blit(texto_p1, (10, 10))
        pantalla.blit(texto_p2, (ANCHO_PANTALLA - texto_p2.get_width() - 10, 10))

        # Indicador de controles (esquina inferior)
        controles = fuente_pequena.render(
            "P1: A/D mover | ESPACIO disparar    P2: Flechas mover | SHIFT DER disparar",
            True,
            (150, 150, 150),
        )
        pantalla.blit(controles, (10, ALTO_PANTALLA - 30))

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
