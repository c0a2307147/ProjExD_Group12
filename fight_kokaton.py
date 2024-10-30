import os
import random
import sys
import time
import pygame as pg


WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
NUM_OF_BOMBS = 5
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとんや爆弾，ビームなどのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


class Bird(pg.sprite.Sprite):
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }
    img0 = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん（右向き）
    imgs = {  # 0度から反時計回りに定義
        (+5, 0): img,  # 右
        (+5, -5): pg.transform.rotozoom(img, 45, 0.9),  # 右上
        (0, -5): pg.transform.rotozoom(img, 90, 0.9),  # 上
        (-5, -5): pg.transform.rotozoom(img0, -45, 0.9),  # 左上
        (-5, 0): img0,  # 左
        (-5, +5): pg.transform.rotozoom(img0, 45, 0.9),  # 左下
        (0, +5): pg.transform.rotozoom(img, -90, 0.9),  # 下
        (+5, +5): pg.transform.rotozoom(img, -45, 0.9),  # 右下
    }

    def __init__(self, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数 xy：こうかとん画像の初期位置座標タプル
        """
        self.image = __class__.imgs[(+5, 0)]
        self.rect: pg.Rect = self.image.get_rect()
        self.rect.center = xy

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.image = pg.transform.rotozoom(
            pg.image.load(f"fig/{num}.png"), 0, 0.9)
        screen.blit(self.image, self.rect)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rect.move_ip(sum_mv)
        if check_bound(self.rect) != (True, True):
            self.rect.move_ip(-sum_mv[0], -sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.image = __class__.imgs[tuple(sum_mv)]
        screen.blit(self.image, self.rect)


class Beam:
    """
    こうかとんが放つビームに関するクラス
    """

    def __init__(self, bird: "Bird"):
        """
        ビーム画像Surfaceを生成する
        引数 bird：ビームを放つこうかとん（Birdインスタンス）
        """
        self.img = pg.image.load(f"fig/beam.png")
        self.rct = self.img.get_rect()
        self.rct.centery = bird.rct.centery
        self.rct.left = bird.rct.right
        self.vx, self.vy = +5, 0

    def update(self, screen: pg.Surface):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        if check_bound(self.rct) == (True, True):
            self.rct.move_ip(self.vx, self.vy)
            screen.blit(self.img, self.rct)


class Bomb:
    """
    爆弾に関するクラス
    """

    def __init__(self, color: tuple[int, int, int], rad: int):
        """
        引数に基づき爆弾円Surfaceを生成する
        引数1 color：爆弾円の色タプル
        引数2 rad：爆弾円の半径
        """
        self.img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.img, color, (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx, self.vy = +5, +5

    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)


class Score:  # 現状問題なし
    def __init__(self):
        self.fonto = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)
        self.img = self.fonto.render("スコア：0", 0, (0, 0, 255))
        self.rct = self.img.get_rect()
        self.rct.center = [100, 50]
        self.point = 0

    def update(self, screen: pg.Surface):
        self.img = self.fonto.render(f"スコア：{self.point}", 0, (0, 0, 255))
        screen.blit(self.img, [100, HEIGHT-50])


class Wall(pg.sprite.Sprite):
    '''
    壁を生成するためのクラスの設置位置
    width: 壁の横幅
    xy: 壁
    height: 壁の縦幅
    '''

    def __init__(self, xy: tuple[int, int], width: int, height: int):
        super().__init__()
        self.image = pg.Surface([width, height])
        pg.draw.rect(self.image, (255, 0, 0), (0, 0, width, height))
        self.rect = self.image.get_rect()
        self.rect.topleft = xy

    def update(self, screen: pg.Surface):
        screen.blit(self.image, self.rect)


class Stage:
    '''
    ステージを生成するためのクラス
    '''

    def __init__(self):
        # 壁のリストを作成
        self.walls = pg.sprite.Group()
        self.goals = pg.sprite.Group()
        # 壁を生成
        wall_settings = [
            ((0, 0), WIDTH, 20),      # 上の壁
            ((0, HEIGHT-20), WIDTH, 20),  # 下の壁
            ((0, 0), 20, HEIGHT),     # 左の壁
            ((WIDTH-20, 0), 20, HEIGHT),  # 右の壁

            ((100, 100), 5, 550),
            ((100, 100), WIDTH-400, 5),
            ((WIDTH-300, 100), 5, HEIGHT-100),
            ((WIDTH-220, 0), 5, HEIGHT)


        ]

        # リストを使って壁を生成
        for setting in wall_settings:
            self.walls.add(Wall(*setting))
        self.goal = Wall((WIDTH-300, HEIGHT-40), 80, 10)
        self.goal.image.fill((0, 255, 0))
        self.goals.add(self.goal)

    def draw_grid(self, screen: pg.Surface, grid_size: int):
        """
        グリッドを描画するメソッド
        引数 screen: 描画対象のSurface
        引数 grid_size: グリッドのサイズ（ピクセル）
        """
        for x in range(0, WIDTH, grid_size):
            pg.draw.line(screen, (0, 0, 0), (x, 0), (x, HEIGHT))  # 垂直線
        for y in range(0, HEIGHT, grid_size):
            pg.draw.line(screen, (0, 0, 0), (0, y), (WIDTH, y))  # 水平線

    def update(self, screen: pg.Surface):
        for wall in self.walls:
            if isinstance(wall, MovingWall):
                wall.update()
        self.walls.draw(screen)
        pg.display.update()


def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bird = Bird((50, HEIGHT-50))
    # beam = None
    # beams = []
    # # bomb = Bomb((255, 0, 0), 10)
    # bombs = [Bomb((255, 0, 0), 10) for _ in range(NUM_OF_BOMBS)]
    stage = Stage()
    score = Score()
    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

            # if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
            #     # スペースキー押下でBeamクラスのインスタンス生成
            #     beam = Beam(bird)
            #     beams.append(beam)
        screen.blit(bg_img, [0, 0])

        # for bomb in bombs:
        #     if bird.rect.colliderect(bomb.rct):
        #         # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
        #         bird.change_img(8, screen)
        #         fonto = pg.font.Font(None, 80)
        #         txt = fonto.render("Game Over", True, (255, 0, 0))
        #         screen.blit(txt, [WIDTH//2-150, HEIGHT//2])
        #         pg.display. update()
        #         time.sleep(5)
        #         return

        # for j, bomb in enumerate(bombs):
        #     for i, beam in enumerate(beams):
        #         if beam is not None:
        #             if beam.rct.colliderect(bomb.rct):
        #                 beams[i], bombs[j] = None, None
        #                 bird.change_img(6, screen)
        #                 score.point += 1
        #                 pg.display.update()
        #     beams = [beam for beam in beams if beam is not None]
        # bombs = [bomb for bomb in bombs if bomb is not None]

        # for i, beam in enumerate(beams):
        #     if check_bound(beam.rct) != (True, True):
        #         beams[i] = None
        #         pg.display.update()
        # beams = [beam for beam in beams if beam is not None]
        if len(pg.sprite.spritecollide(bird, stage.walls, False)) != 0:
            bird.change_img(8, screen)
            fonto = pg.font.Font(None, 80)
            txt = fonto.render("Game Over", True, (255, 0, 0))
            screen.blit(txt, [WIDTH//2-150, HEIGHT//2])
            pg.display.update()
            time.sleep(5)
            return
        if len(pg.sprite.spritecollide(bird, stage.goals, False)) != 0:
            bird.change_img(8, screen)
            fonto = pg.font.Font(None, 80)
            txt = fonto.render("Game Clear", True, (255, 0, 0))
            screen.blit(txt, [WIDTH//2-150, HEIGHT//2])
            pg.display.update()
            time.sleep(5)

        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)
        # for beam in beams:
        #     beam.update(screen)
        # for bomb in bombs:
        #     bomb.update(screen)
        stage.draw_grid(screen, grid_size=100)
        score.update(screen)
        stage.goals.draw(screen)
        stage.walls.draw(screen)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
