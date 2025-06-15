import pygame
import sys
import math

# 初始化
pygame.init()
WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('投籃遊戲')
clock = pygame.time.Clock()

# 顏色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 140, 0)
RED = (255, 0, 0)
BLUE = (0, 120, 255)

# 籃框參數
hoop_width = 100
hoop_height = 20
hoop_y = 200
hoop_x = WIDTH // 2 - hoop_width // 2
hoop_speed = 3

# 籃球參數
ball_radius = 20
ball_x = WIDTH // 2
ball_y = HEIGHT - 100
ball_vx = 0
ball_vy = 0
ball_in_motion = False

dragging = False
start_drag = (0, 0)
end_drag = (0, 0)

# 分數
score = 0
# 關卡進球門檻
ROUND_GOALS = [5, 10, 15]
ROUND_TIME = 15  # 每回合秒數
timer = ROUND_TIME
game_state = 'playing'  # playing, fail, all_success
start_ticks = 0
current_round = 0
round_score = 0

max_power = 30

font = pygame.font.SysFont(None, 48)

power = 0

# 遊戲主迴圈
def main():

    global hoop_x, hoop_speed, ball_x, ball_y, ball_vx, ball_vy, ball_in_motion, dragging, start_drag, end_drag, score, power, timer, game_state, start_ticks, current_round, round_score
    running = True
    while running:
        screen.fill(WHITE)
        # 決定目前回合
        if score < ROUND_GOALS[0]:
            current_round = 0
        elif score < ROUND_GOALS[1]:
            current_round = 1
        elif score < ROUND_GOALS[2]:
            current_round = 2
        # 計時
        if game_state == 'playing':
            if start_ticks == 0:
                start_ticks = pygame.time.get_ticks()
            seconds = (pygame.time.get_ticks() - start_ticks) / 1000
            timer = max(0, ROUND_TIME - int(seconds))
            # 計算本回合進球數
            if current_round == 0:
                round_score = score
            elif current_round == 1:
                # 若剛進入新回合，重設計時器
                if score == ROUND_GOALS[0] and seconds > 0:
                    start_ticks = pygame.time.get_ticks()
                    timer = ROUND_TIME
                    seconds = 0
                round_score = score - ROUND_GOALS[0]
            else:
                if score == ROUND_GOALS[1] and seconds > 0:
                    start_ticks = pygame.time.get_ticks()
                    timer = ROUND_TIME
                    seconds = 0
                round_score = score - ROUND_GOALS[1]
            # 判斷失敗
            if timer == 0:
                if (current_round == 0 and score < ROUND_GOALS[0]) or \
                   (current_round == 1 and score < ROUND_GOALS[1]) or \
                   (current_round == 2 and score < ROUND_GOALS[2]):
                    game_state = 'fail'
            # 判斷全破
            if score >= ROUND_GOALS[2]:
                game_state = 'all_success'

        # 處理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not ball_in_motion and game_state == 'playing':
                if math.hypot(event.pos[0] - ball_x, event.pos[1] - ball_y) < ball_radius:
                    dragging = True
                    start_drag = event.pos
            elif event.type == pygame.MOUSEMOTION and dragging:
                end_drag = event.pos
                dx = end_drag[0] - start_drag[0]
                dy = end_drag[1] - start_drag[1]
                power = min(int(math.hypot(dx, dy)), max_power)
            elif event.type == pygame.MOUSEBUTTONUP and dragging:
                dragging = False
                dx = end_drag[0] - start_drag[0]
                dy = end_drag[1] - start_drag[1]
                angle = math.atan2(-dy, dx)
                power = min(int(math.hypot(dx, dy)), max_power)
                ball_vx = math.cos(angle) * power
                ball_vy = -math.sin(angle) * power
                ball_in_motion = True
            elif event.type == pygame.KEYDOWN:
                if game_state in ['fail', 'all_success'] and event.key == pygame.K_SPACE:
                    # 重新開始
                    score = 0
                    timer = ROUND_TIME
                    game_state = 'playing'
                    start_ticks = 0
                    hoop_x = WIDTH // 2 - hoop_width // 2
                    hoop_speed = 3
                    ball_x = WIDTH // 2
                    ball_y = HEIGHT - 100
                    ball_in_motion = False
                    ball_vx = ball_vy = 0
                    power = 0
                    current_round = 0
                    round_score = 0

        # 籃框移動
        if game_state == 'playing':
            if current_round == 1:
                hoop_speed = 3 if hoop_speed > 0 else -3
                hoop_x += hoop_speed
                if hoop_x <= 0 or hoop_x + hoop_width >= WIDTH:
                    hoop_speed = -hoop_speed
            elif current_round == 2:
                hoop_speed = 3 + (score - ROUND_GOALS[1]) if hoop_speed > 0 else -(3 + (score - ROUND_GOALS[1]))
                hoop_x += hoop_speed
                if hoop_x <= 0 or hoop_x + hoop_width >= WIDTH:
                    hoop_speed = -hoop_speed

        # 籃球運動
        if ball_in_motion and game_state == 'playing':
            ball_x += ball_vx
            ball_y += ball_vy
            ball_vy += 0.5  # 重力
            # 碰到地面重置
            if ball_y > HEIGHT - 100:
                ball_x = WIDTH // 2
                ball_y = HEIGHT - 100
                ball_in_motion = False
                ball_vx = ball_vy = 0
                power = 0
            # 判斷進球
            if (hoop_y < ball_y - ball_radius < hoop_y + hoop_height and
                hoop_x < ball_x < hoop_x + hoop_width):
                score += 1
                ball_x = WIDTH // 2
                ball_y = HEIGHT - 100
                ball_in_motion = False
                ball_vx = ball_vy = 0
                power = 0

        # 畫籃框
        pygame.draw.rect(screen, RED, (hoop_x, hoop_y, hoop_width, hoop_height))
        # 畫籃球
        pygame.draw.circle(screen, ORANGE, (int(ball_x), int(ball_y)), ball_radius)
        # 畫拖曳線
        if dragging:
            pygame.draw.line(screen, BLUE, (ball_x, ball_y), end_drag, 3)
        # 畫力道條
        pygame.draw.rect(screen, BLACK, (50, HEIGHT - 50, 200, 20), 2)
        pygame.draw.rect(screen, BLUE, (50, HEIGHT - 50, int(200 * power / max_power), 20))
        power_text = font.render(f'力道: {power}', True, BLACK)
        screen.blit(power_text, (270, HEIGHT - 60))
        # 畫分數
        score_text = font.render(f'Score: {score}', True, BLACK)
        screen.blit(score_text, (WIDTH - 200, 30))
        # 畫關卡資訊
        round_names = ['Round 1', 'Round 2', 'Round 3']
        round_goal = ROUND_GOALS[current_round] if current_round < 3 else ROUND_GOALS[2]
        round_text = font.render(f'{round_names[current_round]} 進球: {round_score}/{round_goal - (ROUND_GOALS[current_round-1] if current_round>0 else 0)}', True, BLACK)
        screen.blit(round_text, (50, 30))
        # 畫倒數計時
        timer_text = font.render(f'Time: {timer}', True, RED)
        screen.blit(timer_text, (WIDTH//2 - 60, 80))

        # 關卡結束顯示
        if game_state == 'fail':
            fail_text = font.render('challenge failed! ', True, RED)
            screen.blit(fail_text, (WIDTH//2 - 220, HEIGHT//2 - 40))
        elif game_state == 'all_success':
            win_text = font.render('challenge successful!', True, (0,180,0))
            screen.blit(win_text, (WIDTH//2 - 220, HEIGHT//2 - 40))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
