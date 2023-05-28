import os

FZF = False
FZF_OPTS = "--prompt='Select files to restore> ' " + os.environ.get(
    "FZF_MULTI_OPTS", "--multi"
)
try:
    from pyfzf.pyfzf import FzfPrompt

    fzf = FzfPrompt()
    FZF = True
except ModuleNotFoundError:
    pass


class RestoreUsingFzf(object):
    def __init__(self, input, println, restorer, die):
        self.input = input
        self.println = println
        self.restorer = restorer
        self.die = die

    def restore_using_fzf(self, trashed_files, overwrite=False):
        sorted_files = sorted(
            trashed_files, key=lambda x: x.deletion_date, reverse=True
        )
        fzf_entries = []
        for i, tfile in enumerate(sorted_files):
            fzf_entries.append(
                "{} {} {}".format(i, tfile.deletion_date, tfile.original_location)
            )
        selected = fzf.prompt(fzf_entries, FZF_OPTS)
        if selected is None:
            self.println("Exiting")
        else:
            for selection in selected:
                try:
                    index = int(selection.split()[0])
                    self.restorer.restore_trashed_file(sorted_files[index], overwrite)
                except IOError as e:
                    self.die(e)
