text= "이거 진짜별로인줄 알았는데 최고임"
words=["최고"]

def preprocess(text):
    for word in words:
        if word in text and (not f" {word} " in text):
            text= text.replace(word, f" {word} ")

    return text

rlt=preprocess(text)
print(rlt)
