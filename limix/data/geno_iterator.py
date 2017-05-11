class GIter:
    def __init__(self, geno_reader, start=0, end=None, batch_size=1000):
        self.gr = geno_reader
        self.current = start
        if end is None:
            end = self.gr.getSnpInfo().shape[0]
        self.end = end
        self.batch_size = batch_size

    def __iter__(self):
        return self

    def next(self):
        if self.current >= self.end:
            raise StopIteration
        else:
            _end = self.current + self.batch_size
            rv = self.gr.subset_snps(idx_start=self.current, idx_end=_end)
            self.current = _end 
            return rv
