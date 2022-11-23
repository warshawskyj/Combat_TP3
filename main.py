import arcade
import random

# Constants de taille
WIDTH = 800
HEIGHT = 600
HALF_WIDTH = WIDTH / 2
HALF_HEIGHT = HEIGHT / 2
QUARTER_WIDTH = WIDTH / 4
QUARTER_HEIGHT = HEIGHT / 4
COMBAT = 0
PORTES = 1
RÈGLES = '''Pour réussir un combat, il faut que la valeur du dé lancé soit 
supérieure à la force de l’adversaire.  Dans ce cas, le niveau de vie de l’usager est augmenté de la 
force de l’adversaire. Une défaite a lieu lorsque la valeur du dé lancé par l’usager est inférieure ou 
égale à la force de l’adversaire.  Dans ce cas, le niveau de vie de l’usager est diminué de la force de 
l’adversaire. La partie se termine lorsque les points de vie de l’usager tombent sous 0. L’usager peut 
combattre ou éviter chaque adversaire, dans le cas de l’évitement, il y a une pénalité de 1 point de vie.'''

CHOIX = '''Que voulez-vous faire ?\n
	1- Combattre cet adversaire\n
	2- Contourner cet adversaire\n\t et aller ouvrir une autre porte\n
	3- Afficher les règles du jeu\n
	4- Quitter la partie\n'''


def invert(rgb):
    return 255 - rgb[0], 255 - rgb[1], 255 - rgb[2]


class Rectangle:  # objet qui represente un rectangle
    """
    objet qui represente un rectangle dans arcade
        left: position gauche du rectangle
        right: position droite du rectangle
        top: position haute du rectangle
        bottom: position basse du rectangle
    """

    def __init__(self, left, right, top, bottom, color):
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom
        self.color = color
        self.size = (abs(self.right - self.left), abs(self.top - self.bottom))

    def draw(self):
        arcade.draw_lrtb_rectangle_filled(self.left, self.right, self.top, self.bottom, self.color)


class Textbox:
    """
    objet qui represente un rectangle avec du texte a l'intérieur
        left: position gauche du rectangle
        right: position droite du rectangle
        top: position haute du rectangle
        bottom: position basse du rectangle
        color: couleur du rectangle
        text_contents: texte a afficher
        divisor: valeur par laquelle on divise la largeur du rectangle pour obtenir le decalage apres le debut du texte
    """

    def __init__(self, left, right, top, bottom, color, text_contents, divisor=10):
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom
        self.color = color
        self.text_contents = text_contents
        # on divise le width du rectangle par cette valeur pour obtenir le decalage apres le debut du texte
        self.divisor = divisor
        self.rectangle = Rectangle(self.left, self.right, self.top, self.bottom, self.color)  # le rectangle
        self.text = arcade.Text(text=self.text_contents,
                                start_x=self.rectangle.left + self.rectangle.size[0] / self.divisor,
                                start_y=self.rectangle.bottom + self.rectangle.size[1] / 2, anchor_y='center',
                                color=invert(self.color),
                                width=self.rectangle.size[0] - ((self.rectangle.size[0] // self.divisor) * 2),
                                multiline=True)  # position y du text est au centre de la forme

    def draw(self):
        self.rectangle.draw()
        self.text.draw()


class Combat(arcade.Window):
    def __init__(self):
        # initialisation des variables
        self.vies = 20  # joueur commence avec vingt vies
        self.victoires = 0
        self.perdus = 0
        self.jeux = 0
        self.combats = 0
        self.numero_monstre = 0
        self.victoires_consecutives = 0
        self.status = "gagné"  # si le dernier combat a ete gagne ou perdu
        self.de = 0  # valeur du de
        self.died = False  # si le joueur est mort: pour afficher le message de mort
        self.state = PORTES  # etat du jeu
        self.force = random.randint(1, 5)  # la force du monstre actuel
        super().__init__(WIDTH, HEIGHT,
                         "TP2 - Combat")  # initialiser l'objet window avec la taille et le titre
        self.background_color = (133, 132, 138)
        self.combat_sprites = []
        self.life_box_size = 100, 50
        self.vies_sprite = Textbox(0, 150, HEIGHT, HEIGHT - 50, (255, 0, 0), '',
                                   10)  # rectangle dans lequel va se trouver le nombre de vies
        self.choix_sprite = Textbox(HALF_WIDTH - 200, HALF_WIDTH + 200, HALF_HEIGHT + 200, HALF_HEIGHT - 200,
                                    (55, 150, 222), CHOIX)
        self.force_sprite = Textbox(HALF_WIDTH - 60, HALF_WIDTH + 60, self.choix_sprite.rectangle.top + 25,
                                    self.choix_sprite.rectangle.top, (122, 7, 7), '')
        self.choix_sprite.text.width = self.choix_sprite.rectangle.size[0] - (
                (self.choix_sprite.rectangle.size[
                     0] / self.choix_sprite.divisor) * 2)  # modification de la largeur du texte pour qu'il soit plus lisible
        self.choix_sprite.text.bold = True
        self.de_sprite = Textbox(HALF_WIDTH - 60, HALF_WIDTH + 60, 3 * QUARTER_HEIGHT, 3 * QUARTER_HEIGHT - 30,
                                 (122, 7, 7), '')
        self.status_sprite = Textbox(HALF_WIDTH - 200, HALF_WIDTH + 200, self.choix_sprite.rectangle.bottom,
                                     self.choix_sprite.rectangle.bottom - 50, (12, 201, 198), '')
        self.victoire_sprite = Textbox(WIDTH - 150, WIDTH, HEIGHT, HEIGHT - 50, (0, 255, 0), '')
        self.perdu_sprite = Textbox(WIDTH - 150, WIDTH, self.victoire_sprite.bottom, self.victoire_sprite.bottom - 50,
                                    (56, 32, 200), '')
        self.combats_sprite = Textbox(WIDTH - 150, WIDTH, self.perdu_sprite.bottom, self.perdu_sprite.bottom - 50,
                                      (255, 8, 115), '')
        self.numero_monstre_sprite = Textbox(WIDTH - 150, WIDTH, self.combats_sprite.bottom,
                                             self.combats_sprite.bottom - 50,
                                             (32, 105, 7), '')
        self.porte1 = arcade.load_texture("Images/porte_tp3.png", width=171, height=200)  # charger les images
        self.porte2 = arcade.load_texture("Images/porte_tp3.png", width=171, height=200)
        self.death_sprite = Textbox(WIDTH - 50, WIDTH + 50, HEIGHT - 50, HEIGHT - 75, (0, 0, 0), '')
        self.combat_sprites = [self.vies_sprite, self.force_sprite, self.choix_sprite, self.victoire_sprite,
                               self.perdu_sprite, self.combats_sprite, self.numero_monstre_sprite]

    def fight_monster(self):
        self.de = random.randint(1, 6) + random.randint(1, 6)  # on lance les des
        if self.de > self.force:  # joueur a gagne
            self.vies += self.force
            self.victoires += 1
            self.victoires_consecutives += 1
            self.status = "gagné"
        else:  # joueur a perdu
            self.vies -= self.force
            self.perdus += 1
            self.victoires_consecutives = 0  # on remet le nombre de victoires consecutives a zero
            self.status = "perdu"
        self.numero_monstre += 1
        self.combats += 1

    def on_draw(self):
        # dessiner les sprites
        self.clear()
        # update le texte pour mettre a jour les valeurs
        if self.state == COMBAT:
            self.vies_sprite.text.text = f"Vies: {self.vies}"
            self.force_sprite.text.text = f"Force: {self.force}"
            self.victoire_sprite.text.text = f"Victoires: {self.victoires}"
            self.perdu_sprite.text.text = f"Perdus: {self.perdus}"
            self.combats_sprite.text.text = f"Combats: {self.combats}"
            self.numero_monstre_sprite.text.text = f"Monstre: {self.numero_monstre}"
            for sprite in self.combat_sprites:
                sprite.draw()
        else:  # state == PORTES
            if self.died:
                self.death_sprite.text.text = f"Vous êtes mort. Vous avez vaincu {self.victoires} monstres."
                self.death_sprite.draw()
                self.died = False
            self.de_sprite.text.text = f"Dé: {self.de}"
            self.status_sprite.text.text = f"Dernier combat: {self.status}"
            self.de_sprite.draw()
            self.status_sprite.draw()
            self.porte1.draw_scaled(QUARTER_WIDTH, HALF_HEIGHT, 1)
            self.porte2.draw_scaled(QUARTER_WIDTH * 3, HALF_HEIGHT, 1)

    # changer la force du monstre et determiner si le joueur est mort
    def update_jeu(self):
        if self.numero_monstre % 3 == 0:  # un boss
            self.force = random.randint(3, 6) + random.randint(3, 5)  # force entre 6 et 11
        else:
            self.force = random.randint(1, 6) + random.randint(1,5)  # pour avoir une distribution similaire aux des. entre 2 et 11
        self.force = random.randint(1, 11)
        self.choix_sprite.text.text = CHOIX
        self.state = PORTES
        if self.vies <= 0:  # le joueur est mort, recommencer le jeu
            self.died = True
            self.vies = 20
            self.combats = 0
            self.numero_monstre = 0
            self.jeux += 1
            self.victoires = 0
            self.perdus = 0
            self.victoires_consecutives = 0

    def on_key_press(self, symbol: int, modifiers: int):
        self.choix_sprite.text.text = CHOIX
        if self.state == COMBAT:
            if symbol == 49:  # 1 > combattre le monstre
                self.fight_monster()
                self.update_jeu()
            elif symbol == 50:  # 2 > fuir
                self.vies -= 1
                self.victoires_consecutives = 0  # on remet le nombre de victoires consecutives a zero
                self.numero_monstre += 1
                self.update_jeu()
            elif symbol == 51:  # 3 > afficher les regles
                self.choix_sprite.text.text = RÈGLES
            elif symbol == 52:  # 4 > quitter
                print("Au revoir")
                arcade.close_window()
        else:  # state = PORTES
            self.state = COMBAT


def main():
    Combat()
    arcade.run()


if __name__ == "__main__":
    main()
