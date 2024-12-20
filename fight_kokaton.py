import os
import random
import sys
import time
import math
import pygame as pg

WIDTH = 1100  # ゲームウィンドウの幅
HEIGHT = 650  # ゲームウィンドウの高さ
MARGIN = 50  # 壁と画面の間の隙間
THINKNESS = 5  # 壁の太さ
NUM_OF_BOMBS = 17  # ボムの個数

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


class Timer:
    def __init__(self):
        self.font = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)
        self.start_time = time.time()
        self.elapsed_time = 0

    def update(self, screen: pg.Surface):
        self.elapsed_time = time.time() - self.start_time
        # Convert elapsed time to minutes and seconds (adjust as needed)
        minutes = int(self.elapsed_time // 60)
        seconds = int(self.elapsed_time % 60)
        timer_text = f"Time: {minutes:02d}:{seconds:02d}"
        self.img = self.font.render(timer_text, True, (0, 0, 255))
        self.rect = self.img.get_rect()
        self.rect.center = [120, 30]  # Adjust position as needed
        screen.blit(self.img, self.rect)


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
        self.image = pg.transform.rotozoom(pg.image.load(f"fig/3.png"), 0, 0.9)
        self.rect = self.image.get_rect()
        self.rect.center = xy

        self.invincible = False
        self.invincible_timer = 0
        self.invincible_duration = 2500

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.image = pg.transform.rotozoom(
            pg.image.load(f"fig/{num}.png"), 0, 0.9)
        screen.blit(self.image, self.rect)
    # 無敵じゃなかったらライフを減らす
    def check_invincible(self, heart):
        if not self.invincible:
            heart.life -= 1
            heart.display()
            self.effect_invincible()
    # 無敵状態にする
    def effect_invincible(self):
        self.invincible = True
        self.invincible_timer = pg.time.get_ticks()


    def check_heart(self, screen, heart):
        # ライフが0になったらゲームオーバー
        if heart.life <= 0:
            fonto = pg.font.Font(None, 80)
            txt = fonto.render("Game Over", True, (255, 0, 0))
            screen.blit(txt, [WIDTH//2-150, HEIGHT//2])
            pg.display.update()
            time.sleep(3)
            # ゲームオーバー時にはmain関数を再帰呼び出し(後で変えるかも)
            return main()

    def update(self, key_lst: list[bool], screen: pg.Surface, walls: pg.sprite.Group, m_walls: pg.sprite.Sprite, heart: int) -> list[int]:
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        引数3 walls：壁のグループ
        引数4 heart：ライフ表示用HEARTクラスインスタンス
        戻り値：横方向，縦方向の移動量リスト
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rect.move_ip(sum_mv)
        # 壁との衝突判定
        if pg.sprite.spritecollide(self, walls, False) or pg.sprite.spritecollide(self, m_walls, False):
            # 衝突時には移動を戻す
            self.rect.move_ip(-sum_mv[0], -sum_mv[1])
            sum_mv = [0, 0]
            # 無敵状態でない場合はライフを減らす
            self.check_invincible(heart)
            self.check_heart(screen, heart)

        if check_bound(self.rect) != (True, True):
            self.rect.move_ip(-sum_mv[0], -sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.image = __class__.imgs[tuple(sum_mv)]
        if self.invincible:
            # 現在の時間を取得
            current_time = pg.time.get_ticks()
            # 無敵状態の時間が経過したら無敵状態を解除
            if current_time - self.invincible_timer > self.invincible_duration:
                self.invincible = False
            else:
                # 200ミリ秒ごとに画像を切り替えて点滅させる
                if (current_time // 200) % 2 == 0:
                    screen.blit(pg.transform.laplacian(self.image), self.rect)
                else:
                    screen.blit(self.image, self.rect)
        else:
            screen.blit(self.image, self.rect)
        return sum_mv


class MovingWall(pg.sprite.Sprite):
    def __init__(self, left_limit: int, right_limit: int, y: int, width: int, height: int, sp: int):
        super().__init__()
        self.image = pg.Surface((width, height))
        self.image.fill((255, 0, 0))  # 赤色で塗りつぶす
        self.rect = self.image.get_rect()  # 初期位置を左右の限界値の中央に設定
        center_x = (left_limit + right_limit - width) // 2
        self.rect.topleft = (center_x, y)
        self.sp = sp
        self.direction = 1
        self.left_limit = left_limit
        self.right_limit = right_limit

    def update(self, screen: pg.Surface):  # 壁を左右に移動させる
        self.rect.x += self.sp * self.direction  # 壁の移動範囲を制御する
        if self.rect.right >= self.right_limit or self.rect.left <= self.left_limit:
            self.direction *= -1  # 方向を反転させる
            # 壁を描画する
            screen.blit(self.image, self.rect)


# class Beam:
#     """
#     こうかとんが放つビームに関するクラス
#     """

#     def __init__(self, bird:  Bird):
#         """
#         ビーム画像Surfaceを生成する
#         引数 bird：ビームを放つこうかとん（Birdインスタンス）
#         """
#         self.img = pg.image.load(f"fig/beam.png")
#         self.rct = self.img.get_rect()
#         self.rct.centery = bird.rct.centery
#         self.rct.left = bird.rct.right
#         self.vx, self.vy = +5, 0

#     def update(self, screen: pg.Surface):
#         """
#         ビームを速度ベクトルself.vx, self.vyに基づき移動させる
#         引数 screen：画面Surface
#         """
#         if check_bound(self.rct) == (True, True):
#             self.rct.move_ip(self.vx, self.vy)
#             screen.blit(self.img, self.rct)


class Bomb:
    """
    爆弾に関するクラス
    """

    def __init__(self, color: tuple[int, int, int], rad: int, xy: tuple[int, int]):
        """
        引数に基づき爆弾円Surfaceを生成する
        引数1 color：爆弾円の色タプル
        引数2 rad：爆弾円の半径
        """
        self.img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.img, color, (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = xy  # 画面中央から開始
        self.speed = 3
        self.angle = random.uniform(0, 2 * math.pi)  # ランダムな角度

    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rct.centerx += self.speed * math.cos(self.angle)
        self.rct.centery += self.speed * math.sin(self.angle)
        screen.blit(self.img, self.rct)


# class Score:
#     def __init__(self):
#         self.font = pg.font.Font(None, 50)
#         self.color = (0, 0, 255)
#         self.score = 0
#         self.image = self.font.render(f"Score: {self.score}", 0, self.color)
#         self.rect = self.image.get_rect()
#         self.rect.center = 100, HEIGHT-50

#     def update(self, screen: pg.Surface):
#         self.img = self.fonto.render(f"スコア：{self.point}", 0, (0, 0, 255))
#         screen.blit(self.img, [100, HEIGHT-50])
#     def update(self, screen: pg.Surface):
#         self.image = self.font.render(f"Score: {self.score}", 0, self.color)
#         screen.blit(self.image, self.rect)


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
    level: ステージのレベル
    '''

    def __init__(self, level: int = 1):
        # ステージのレベルを設定
        self.level = level
        # 壁とゴールのグループを作成
        self.walls = pg.sprite.Group()
        self.movingWalls = pg.sprite.Group()
        self.goals = pg.sprite.Group()
        # ステージを作成
        self.create_stage()
    # ステージを作成するメソッド

    def create_stage(self) -> None:
        # 壁とゴールを初期化
        self.walls.empty()
        self.movingWalls.empty()
        self.goals.empty()
        # 外壁の設定(ステージ共通)
        outer_walls = [
            ((MARGIN, MARGIN), WIDTH - 2 * MARGIN, THINKNESS),
            ((MARGIN, HEIGHT - MARGIN - THINKNESS), WIDTH - 2 * MARGIN, THINKNESS),
            ((MARGIN, MARGIN), THINKNESS, HEIGHT - 2 * MARGIN),
            ((WIDTH - MARGIN - THINKNESS, MARGIN), THINKNESS, HEIGHT - 2 * MARGIN)
        ]
        # 外壁を作成
        for wall in outer_walls:
            self.walls.add(Wall(*wall))
        # ステージレベルに応じて内壁とゴールを作成
        match self.level:
            case 1:
                self.create_stage1()
            case 2:
                self.create_stage2()
            case 3:
                self.create_stage3()
    # ステージ1の壁とゴールの設定

    def create_stage1(self) -> None:
        # 初心者向けのステージ
        inner_walls = [
            ((150, 150), THINKNESS, 450),
            ((150, 150), 700, THINKNESS),
            ((WIDTH - 250, 150), THINKNESS, HEIGHT - MARGIN - 150),
            ((WIDTH - 170, 50), THINKNESS, 520),
        ]
        # 内壁を作成
        for wall in inner_walls:
            self.walls.add(Wall(*wall))
        # ゴールを作成,設置
        self.goal = Wall((WIDTH - 250, HEIGHT - 90), 80, 10)
        self.goal.image.fill((0, 255, 0))
        self.goals.add(self.goal)

    # ステージ2の壁とゴールの設定

    def create_stage3(self) -> None:
        # 動く壁もあるステージ、上級者向け
        inner_walls = [
            ((50, HEIGHT-150), 250, THINKNESS),
            ((300, HEIGHT-250), THINKNESS, 100),
            ((300, HEIGHT-250), 100, THINKNESS),
            ((400, HEIGHT-250), THINKNESS, 100),
            ((400, HEIGHT-150), 250, THINKNESS),
            ((650, HEIGHT-250), THINKNESS, 100),
            ((650, HEIGHT-250), 100, THINKNESS),
            ((750, HEIGHT-250), THINKNESS, 100),
            ((750, HEIGHT-150), 200, THINKNESS),

            ((120, 330), WIDTH-170, THINKNESS),
            ((120, 120), THINKNESS, 210),
            ((190, 50), THINKNESS, 160),
            ((190, 300), THINKNESS, 50),
            ((190, 210), 860, THINKNESS),
            # ((190, 300), 860, THINKNESS),
        ]
        # 動く壁の設定
        moving_walls = [
            (WIDTH//2, WIDTH-100, HEIGHT-150, THINKNESS, 100, 2),
            (260, WIDTH//2-100, HEIGHT-150, THINKNESS, 100, 0.6),
            (250, WIDTH-280, HEIGHT-380, THINKNESS, 140, 4),
            (250, WIDTH//2, 200, THINKNESS, 50, -2),
            ((WIDTH-100)//2, WIDTH-100, 200, THINKNESS, 50, 2),
        ]
        # 内壁を作成
        for wall in inner_walls:
            self.walls.add(Wall(*wall))
        # 動く壁を作成
        for m_wall in moving_walls:
            self.movingWalls.add(MovingWall(*m_wall))
        # ゴールを作成,設置
        self.goal = Wall((WIDTH - 60, 210), 10, 100)
        self.goal.image.fill((0, 255, 0))
        self.goals.add(self.goal)
    # ステージ3の壁とゴールの設定

    def create_stage2(self) -> None:
        # 高難易度のステージ、中級者向け
        inner_walls = [
            ((150, HEIGHT-250), THINKNESS, 200),
            ((50, HEIGHT-320), 170, THINKNESS),
            ((220, 50), THINKNESS, 330),
            ((150, HEIGHT-200), 150, THINKNESS),
            ((300, 250), THINKNESS, 200),
            ((220, 180), 430, THINKNESS),
            ((650, 150), 100, THINKNESS),
            ((750, 180), 300, THINKNESS),
            ((300, 250), 650, THINKNESS),
            ((300, HEIGHT-250), 750, THINKNESS),
        ]
        moving_walls = [
            (400, WIDTH-100, 230, THINKNESS, 100, 2),
        ]
        # 内壁を作成
        for wall in inner_walls:
            self.walls.add(Wall(*wall))
        for m_wall in moving_walls:
            self.movingWalls.add(MovingWall(*m_wall))
        # ゴールを作成,設置
        self.goal = Wall((350, 300), 10, 50)
        self.goal.image.fill((0, 255, 0))
        self.goals.add(self.goal)
    # 次のステージに進めるかどうかを判定しながら，ステージを作成するメソッド

    def next_level(self) -> bool:
        '''
        ステージを次のレベルに進めるメソッド
        戻り値：すべてのステージをクリアした場合はFalse，それ以外はTrue
        次にステージに進めるかどうかの真理値だから
        '''
        self.level += 1
        if self.level > 3:
            return False
        self.create_stage()
        return True
    # gridを描画するメソッド

    def draw_grid(self, screen: pg.Surface, grid_size: int) -> None:
        """
        ステージを作成するときの目安になるGridを描画するメソッド
        引数 screen: 描画対象のSurface
        引数 grid_size: グリッドのサイズ（ピクセル）
        本番環境では使わない
        """
        MARGIN = 0  # 壁と画面の間の隙間
        THINKNESS = 10  # 壁の太さ
        for x in range(MARGIN, WIDTH - MARGIN, grid_size):
            pg.draw.line(screen, (0, 0, 0), (x, MARGIN),
                         (x, HEIGHT - MARGIN), 1)
        for y in range(MARGIN, HEIGHT - MARGIN, grid_size):
            pg.draw.line(screen, (0, 0, 0), (MARGIN, y),
                         (WIDTH - MARGIN, y), 1)
    # ステージを描画するメソッド

    def update(self, screen: pg.Surface) -> None:
        for wall in self.walls:
            if isinstance(wall, MovingWall):
                wall.update()
        self.walls.draw(screen)
        pg.display.update()


class HEART:
    '''
    ライフを表示するためのクラス
    '''
    # ライフの初期値
    life = 5

    def __init__(self, screen: pg.Surface):
        self.screen = screen
        self.font = pg.font.Font(None, 36)
        life_text = self.font.render(f"Life: {self.life}", True, (0, 0, 0))
        self.screen.blit(life_text,  [250, 20])
    # ライフを更新し，画面に表示するメソッド

    def display(self):
        life_text = self.font.render(f"Life: {self.life}", True, (0, 0, 0))
        self.screen.blit(life_text,  [250, 20])


def main():
    pg.display.set_caption("すすめ！こうかとん、やっぱりもどれ！")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.Surface((WIDTH, HEIGHT))
    bg_img.fill((255, 255, 255))
    bird = Bird((110, HEIGHT-90))
    # movingwall = MovingWall(400, 100, 20, 80, 3)
    # movingwall_2 = MovingWall(500, 300, 20, 80, 3)
    # HEARTクラスのインスタンス生成
    heart = HEART(screen)
    # beam = None
    # beams = []

    bombs = []
    # ステージクラスのインスタンス生成
    stage = Stage()
    # score = Score()
    clock = pg.time.Clock()
    tmr = 0
    last_bomb_time = 0

    # 中心点の黒い円を描画するための設定
    center_circle = pg.Surface((40, 40), pg.SRCALPHA)
    pg.draw.circle(center_circle, (0, 0, 0), (20, 20), 30)

    timer = Timer()
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

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
        # ゴールに到達した場合
        if len(pg.sprite.spritecollide(bird, stage.goals, False)) != 0:
            # 次のステージに進めない場合はすべてのステージをクリアしたことになる
            if not stage.next_level():
                # すべてのステージをクリアしたことを表示
                bird.change_img(9, screen)
                fonto = pg.font.Font(None, 80)
                txt = fonto.render("All Stages Clear!", True, (0, 0, 255))
                screen.blit(txt, [WIDTH//2-150, HEIGHT//2])
                pg.display.update()
                # 3秒間表示させる
                time.sleep(3)
                return main()
            else:
                # それ以外はこのステージをクリアしたことを表示
                for bomb in bombs:
                    bombs.remove(bomb)
                fonto = pg.font.Font(None, 80)
                txt = fonto.render("Stage Clear!", True, (0, 0, 255))
                screen.blit(txt, [WIDTH//2-150, HEIGHT//2])
                bird.rect.center = (110, HEIGHT-90)
                # 端末によって次のステージに進むときに前の移動量が残っておりダメージを受けてしまうので無敵化
                bird.effect_invincible()
                # 難易度を下げるためにライフを回復
                heart.life+=1
                pg.display.update()
                time.sleep(0.9)

        if stage.level == 1:
            screen.blit(center_circle, (WIDTH//2 - 20, HEIGHT//2 - 20))
            if tmr - last_bomb_time >= 20:  # 約1秒ごとに新しい爆弾を生成（元50）
                if len(bombs) < NUM_OF_BOMBS:
                    bombs.append(Bomb((255, 0, 0), 10, (WIDTH//2, HEIGHT//2)))
                last_bomb_time = tmr
        elif stage.level == 2:
            screen.blit(center_circle, (WIDTH//2-20, HEIGHT - 170))
            if tmr - last_bomb_time >= 20:
                if len(bombs) < NUM_OF_BOMBS:
                    bombs.append(Bomb((255, 0, 0), 10, (WIDTH//2, HEIGHT-150)))
                last_bomb_time = tmr
        for bomb in bombs[:]:
            bomb.update(screen)
            if bomb.rct.colliderect(bird.rect):
                bombs.remove(bomb)
                bird.change_img(8, screen)
                bird.check_invincible(heart)
                bird.check_heart(screen, heart)
            if check_bound(bomb.rct) != (True, True):
                bombs.remove(bomb)
        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen, stage.walls, stage.movingWalls, heart)
        # for beam in beams:
        #     beam.update(screen)
        # for bomb in bombs:
        #     bomb.update(screen)
        # 開発時にはGridを表示
        # stage.draw_grid(screen, grid_size=50)
        # score.update(screen)
        # ライフの表示,更新
        heart.display()

        # ステージとゴールを描画
        stage.goals.draw(screen)

        stage.movingWalls.draw(screen)
        stage.movingWalls.update(screen)
        stage.walls.draw(screen)
        # bird.update(key_lst, screen,walls,m_walls,heart)
        # for beam in beams :
        #     beam.update(screen)
        # for bomb in bombs:
        #     bomb.update(screen)
        # score.update(screen)

        timer_text = timer.update(screen)  # Update the timer and get the text

        # Display the timer text separately to ensure it's always visible
        # You can customize the position and style as needed
        font = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)
        text_surface = font.render(timer_text, True, (255, 255, 255))
        screen.blit(text_surface, (10, 10))
        pg.display.update()
        # clock.tick(50)
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
