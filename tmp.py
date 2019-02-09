from goto import with_goto


@with_goto
def Test():
    label.start
    print('start...')
    label.step1
    print('step1')
    label.step2
    print('step2')
    goto.start


Test()
