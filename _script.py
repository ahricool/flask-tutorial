import click
import logging
import _script2

@click.command()
@click.option('-ww',is_flag=True)
# @click.option('-w','--ww')
@click.option('-p','--param',default=100)
def run(ww,param):
    print((ww,param))



if __name__=='__main__':


    run()

