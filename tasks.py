from invoke import task


@task
def bumpversion(c, version):
    c.run(f"bumpversion {version}")
    # c.run("git push origin -o ci.skip")
    # c.run("git push origin --tags")
