import pygame


def getFontSize(font_, text_, color_):
    sprite = font_.render(text_, True, color_)
    return [sprite.get_width(), sprite.get_height()]


def simpleText(screen_, color_, font_, x_, y_, text_):
    screen_.blit(font_.render(text_, True, color_), (x_, y_))


def getFontSizeWithWrap(font_, text_, max_len):
    out = []
    complete_row = ""
    if pygame.font.Font.size(font_, text_)[0] > max_len:
        all_words = []
        word = ""
        complete_row = ""
        for i, char in enumerate(text_):
            if char != " ":
                word += char
            else:
                all_words.append(word + " ")
                word = ""
            if i + 1 == len(text_):
                all_words.append(word)
        for i, word in enumerate(all_words):
            if pygame.font.Font.size(font_, word)[0] + pygame.font.Font.size(font_, complete_row)[0] > max_len:
                out.append(complete_row)
                complete_row = "" + word
            else:
                complete_row += word
            if i + 1 == len(all_words):
                complete_row += word
    else:
        complete_row += text_
    out.append(complete_row)
    largest_len = max([pygame.font.Font.size(font_, line)[0] for line in out])
    return [len(out), largest_len]


def draw_text(screen_, color_, font_, x_, y_, text_, color2_=None, shadow_size_=0, wrap_=False, max_len=None, centered_=False):
    if wrap_:
        if pygame.font.Font.size(font_, text_)[0] > max_len:
            all_words = []
            temp = ""
            complete_row = ""
            output = []
            for i, char in enumerate(text_):
                if char != " ":
                    temp += char
                else:
                    all_words.append(temp + " ")
                    temp = ""
                if i + 1 == len(text_):
                    all_words.append(temp)
            for i, word in enumerate(all_words):
                if pygame.font.Font.size(font_, word)[0] + pygame.font.Font.size(font_, complete_row)[0] > max_len:
                    output.append(complete_row)
                    complete_row = "" + word
                else:
                    complete_row += word
            output.append(complete_row)
            if centered_:
                for i, row in enumerate(output):
                    if shadow_size_ != 0:
                        screen_.blit(font_.render(row, True, color2_), (x_ - pygame.font.Font.size(font_, row)[0] / 2 + shadow_size_, y_ + shadow_size_ + ((i - len(output) / 2) * 1.1 * pygame.font.Font.size(font_, row)[1])))
                    screen_.blit(font_.render(row, True, color_), (x_ - pygame.font.Font.size(font_, row)[0] / 2, y_ + ((i - len(output) / 2) * 1.1 * pygame.font.Font.size(font_, row)[1])))
            else:
                for i, row in enumerate(output):
                    if shadow_size_ != 0:
                        screen_.blit(font_.render(row, True, color2_), (x_ + shadow_size_, y_ + shadow_size_ + (i * 1.1 * pygame.font.Font.size(font_, row)[1])))
                    screen_.blit(font_.render(row, True, color_), (x_, y_ + (i * 1.1 * pygame.font.Font.size(font_, row)[1])))
        else:
            if centered_:
                if shadow_size_ != 0:
                    screen_.blit(font_.render(text_, True, color2_), (x_ - pygame.font.Font.size(font_, text_)[0] / 2 + shadow_size_, y_ - pygame.font.Font.size(font_, text_)[1] / 2 + shadow_size_))
                screen_.blit(font_.render(text_, True, color_), (x_ - pygame.font.Font.size(font_, text_)[0] / 2, y_ - pygame.font.Font.size(font_, text_)[1] / 2))
            else:
                if shadow_size_ != 0:
                    screen_.blit(font_.render(text_, True, color2_), (x_ + shadow_size_, y_ + shadow_size_))
                screen_.blit(font_.render(text_, True, color_), (x_, y_))
    else:
        if centered_:
            if shadow_size_ != 0:
                screen_.blit(font_.render(text_, True, color2_), (x_ - pygame.font.Font.size(font_, text_)[0] / 2 + shadow_size_, y_ - pygame.font.Font.size(font_, text_)[1] / 2 + shadow_size_))
            screen_.blit(font_.render(text_, True, color_), (x_ - pygame.font.Font.size(font_, text_)[0] / 2, y_ - pygame.font.Font.size(font_, text_)[1] / 2))
        else:
            if shadow_size_ != 0:
                screen_.blit(font_.render(text_, True, color2_), (x_ + shadow_size_, y_ + shadow_size_))
            screen_.blit(font_.render(text_, True, color_), (x_, y_))
