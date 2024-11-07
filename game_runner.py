import pygame
import os
from typing import Dict, List, Optional
import random

class GameRunner:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # 画面設定
        self.base_width = 320
        self.base_height = 200
        self.setup_display()
        
        # ゲーム設定
        self.settings = {
            'scroll_speed': 2 * self.scale_factor,
            'jump_speed': -15,
            'gravity': 1.35,
            'obstacle_speed': 5 * self.scale_factor
        }
        
        # フェード設定
        self.fade_duration = 10000
        self.fade_start_time = 0
        
        # 背景スクロール位置
        self.bg_x1 = 0
        self.bg_x2 = self.width
        
        # アセット読み込み
        self.load_assets()
        
        # ゲーム状態
        self.reset_game_state()

    def setup_display(self) -> None:
        pygame.display.gl_set_attribute(pygame.GL_DOUBLEBUFFER, 1)
        os.environ['SDL_VIDEO_SYNCHRONIZED'] = '1'
        info = pygame.display.Info()
        self.scale_factor = min(
            info.current_w / self.base_width,
            info.current_h / self.base_height
        )
        self.width = int(self.base_width * self.scale_factor)
        self.height = int(self.base_height * self.scale_factor)
        self.screen = pygame.display.set_mode(
            (self.width, self.height),
            pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.SCALED
        )
        pygame.display.set_caption("Rhythm Game")

    def load_assets(self) -> None:
        self.images = {
            'player': self.load_image('player.png', 
                (int(48 * self.scale_factor), int(64 * self.scale_factor))),
            'background': self.load_image('background.png', 
                (self.width, self.height)),
            'obstacles': self.load_obstacle_images()
        }
        
    def load_image(self, image_name: str, size: tuple) -> Optional[pygame.Surface]:
        try:
            image_path = os.path.join('assets', 'images', image_name)
            return pygame.transform.scale(
                pygame.image.load(image_path), size
            )
        except Exception as e:
            print(f"画像読み込みエラー: {image_path} - {str(e)}")
            return None

    def load_obstacle_images(self) -> List[pygame.Surface]:
        obstacles_path = os.path.join('assets', 'images', 'obstacles')
        images = []
        if os.path.exists(obstacles_path):
            for file in os.listdir(obstacles_path):
                if file.lower().endswith('.png'):
                    img = self.load_image(
                        os.path.join('obstacles', file),
                        (int(28 * self.scale_factor), 
                         int(48 * self.scale_factor))
                    )
                    if img:
                        images.append(img)
        return images

    def reset_game_state(self) -> None:
        self.player = {
            'x': int(40 * self.scale_factor),
            'y': self.height - int(64 * self.scale_factor) - int(10 * self.scale_factor),
            'velocity': 0
        }
        self.obstacles = []
        self.score = 0
        self.passed_obstacles = set()
        self.game_over = False
        self.game_clear = False
        self.rhythm_index = 0
        self.bg_x1 = 0
        self.bg_x2 = self.width
        self.fade_start_time = 0

    def run(self, song_path: str, rhythm_data: Dict) -> None:
        self.reset_game_state()
        clock = pygame.time.Clock()
        
        pygame.mixer.music.load(song_path)
        start_time = pygame.time.get_ticks() + 3000
        pygame.mixer.music.play(start=0, fade_ms=0)
        pygame.mixer.music.pause()
        
        game_ready = False
        
        while True:
            current_time = pygame.time.get_ticks()
            
            if self.handle_events():
                pygame.mixer.music.stop()
                break
            
            # 背景スクロール
            self.bg_x1 -= self.settings['scroll_speed']
            self.bg_x2 -= self.settings['scroll_speed']
            if self.bg_x1 <= -self.width:
                self.bg_x1 = self.width
            if self.bg_x2 <= -self.width:
                self.bg_x2 = self.width
            
            # 背景描画
            if self.images['background']:
                self.screen.blit(self.images['background'], (self.bg_x1, 0))
                self.screen.blit(self.images['background'], (self.bg_x2, 0))
            else:
                self.screen.fill((255, 255, 255))
            
            # プレイヤーの物理演算
            self.player['velocity'] += self.settings['gravity'] * self.scale_factor
            self.player['y'] += self.player['velocity']
            if self.player['y'] > self.height - int(64 * self.scale_factor) - int(10 * self.scale_factor):
                self.player['y'] = self.height - int(64 * self.scale_factor) - int(10 * self.scale_factor)
                self.player['velocity'] = 0
            
            # プレイヤー描画
            if self.images['player']:
                self.screen.blit(
                    self.images['player'],
                    (self.player['x'], self.player['y'])
                )
            
            if not game_ready:
                if current_time >= start_time:
                    game_ready = True
                    pygame.mixer.music.unpause()
                else:
                    countdown = str(3 - (current_time - (start_time - 3000)) // 1000)
                    self.draw_countdown(countdown)
            else:
                self.update_game_state((current_time - start_time) / 1000, rhythm_data)
                self.draw()
                
                if self.game_clear:
                    current_fade_time = pygame.time.get_ticks() - self.fade_start_time
                    if current_fade_time <= self.fade_duration:
                        volume = 1.0 - (current_fade_time / self.fade_duration)
                        pygame.mixer.music.set_volume(volume)
            
            pygame.display.flip()
            clock.tick(60)

    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and 
                event.key == pygame.K_ESCAPE
            ):
                return True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.player['y'] >= self.height - int(64 * self.scale_factor) - int(10 * self.scale_factor):
                        self.player['velocity'] = self.settings['jump_speed'] * self.scale_factor
        return False

    def update_game_state(self, current_time: float, rhythm_data: Dict) -> None:
        if self.game_over or self.game_clear:
            return
            
        # 障害物の更新
        self.update_obstacles(current_time, rhythm_data)
        
        # 衝突判定
        self.check_collisions()

        # クリア判定
        if (self.rhythm_index >= len(rhythm_data['rhythm_patterns']) and 
            len(self.passed_obstacles) == len(rhythm_data['rhythm_patterns'])):
            self.game_clear = True
            self.fade_start_time = pygame.time.get_ticks()

    def update_obstacles(self, current_time: float, rhythm_data: Dict) -> None:
        # 既存の障害物を移動
        for obstacle in self.obstacles:
            obstacle['x'] -= self.settings['obstacle_speed']
            
        # 新しい障害物の生成
        if (self.rhythm_index < len(rhythm_data['rhythm_patterns']) and 
            current_time >= rhythm_data['rhythm_patterns'][self.rhythm_index]['jump_time']):
            
            self.obstacles.append({
                'x': self.width,
                'y': self.height - int(48 * self.scale_factor) - int(10 * self.scale_factor),
                'image': random.choice(self.images['obstacles']) 
                    if self.images['obstacles'] else None
            })
            self.rhythm_index += 1

    def check_collisions(self) -> None:
        player_rect = self.get_collision_rect(
            pygame.Rect(
                self.player['x'], 
                self.player['y'],
                48 * self.scale_factor,
                64 * self.scale_factor
            )
        )
        
        for i, obstacle in enumerate(self.obstacles):
            obstacle_rect = self.get_collision_rect(
                pygame.Rect(
                    obstacle['x'],
                    obstacle['y'],
                    28 * self.scale_factor,
                    48 * self.scale_factor
                )
            )
            
            if player_rect.colliderect(obstacle_rect):
                self.game_over = True
                return
                
            if i not in self.passed_obstacles and obstacle['x'] < self.player['x']:
                self.score += 1
                self.passed_obstacles.add(i)

    def get_collision_rect(self, visual_rect: pygame.Rect) -> pygame.Rect:
        reduction = 0.25
        width_reduction = visual_rect.width * reduction
        height_reduction = visual_rect.height * reduction
        
        return pygame.Rect(
            visual_rect.x + width_reduction,
            visual_rect.y + height_reduction,
            visual_rect.width - (width_reduction * 2),
            visual_rect.height - (height_reduction * 2)
        )

    def draw(self) -> None:
        # 障害物描画
        for obstacle in self.obstacles:
            if obstacle['image']:
                self.screen.blit(
                    obstacle['image'],
                    (obstacle['x'], obstacle['y'])
                )
            
        # スコア表示
        font = pygame.font.Font(None, int(36 * self.scale_factor))
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (self.width * 0.02, self.height * 0.02))
        
        # ゲームオーバー表示
        if self.game_over:
            self.draw_game_over()
            
        # クリア表示
        if self.game_clear:
            self.draw_game_clear()

    def draw_countdown(self, countdown: str) -> None:
        font = pygame.font.Font(None, int(72 * self.scale_factor))
        text = font.render(countdown, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(text, text_rect)

    def draw_game_over(self) -> None:
        font = pygame.font.Font(None, int(72 * self.scale_factor))
        text = font.render("Game Over", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(text, text_rect)

    def draw_game_clear(self) -> None:
        font = pygame.font.Font(None, int(72 * self.scale_factor))
        text = font.render("CLEAR!", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(text, text_rect)

    def update_settings(self, settings: Dict) -> None:
        self.settings.update(settings)



