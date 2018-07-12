# Copyright: 2018, CCX Technologies

from .nft import nft


class Set:

    initialized = False

    def __init__(
            self,
            name,
            table,
            type_,
            flag_constant=False,
            flag_interval=False,
            flag_timeout=False,
            timeout=None,
            gc_interval=None,
            elements=None,
            size=None,
            policy='performance',
            auto_merge=False
    ):
        """Named sets are sets that need to be defined first before they can be
        referenced in rules. Unlike anonymous sets, elements can be added to or
        removed from a named set at any time."""

        self.name = name
        self.table = table.name
        self.family = table.family

        if type_ not in (
                'ipv4_addr', 'ipv6_addr', 'ether_addr', 'inet_proto',
                'inet_service', 'mark'
        ):
            raise RuntimeError(f"Invalid type {type_}")

        self.config = []
        self.config.append(f"type {type_};")

        flags = []
        if flag_constant:
            flags.append('constant')
        if flag_interval:
            flags.append('interval')
        if flag_timeout:
            flags.append('timeout')
        if flags:
            self.config.append(f"flags {','.join(flags)};")

        if timeout:
            self.config.append(f"timeout {timeout};")

        if gc_interval:
            self.config.append(f"gc-interval {gc_interval};")

        if elements:
            self.config.append(f"elements = {{ {','.join(elements)} }};")

        if size:
            self.config.append(f"size {size};")

        if policy:
            self.config.append(f"policy {policy};")

        if auto_merge:
            self.config.append(f"auto-merge;")

    async def load(self):
        """Load the set, must be called before calling any other methods."""

        if self.initialized:
            return

        await nft(
                'add', 'set', self.family, self.table, self.name,
                f"{{ {' '.join(self.config)} }}"
        )

        self.initialized = True

    async def flush(self):
        """Flush all elements of the chain."""
        if not self.initialized:
            raise RuntimeError(f"Set {self.name} hasn't been loaded.")

        await nft('flush', 'set', self.family, self.table, self.name)

    async def delete(self):
        """Delete the set, any subsequent calls to this chain will fail."""
        if not self.initialized:
            raise RuntimeError(f"Set {self.name} hasn't been loaded.")

        await self.flush()
        await nft('delete', 'set', self.family, self.table, self.name)

        self.initialized = False

    async def list(self):
        """List all elements of the set."""
        return await nft('list', 'set', self.family, self.table, self.name)

    async def add_elements(self, elements):
        """Add a list of elements to the set."""
        if not self.initialized:
            raise RuntimeError(f"Set {self.name} hasn't been loaded.")

        await nft(
                'add', 'element', self.family, self.table, self.name,
                f"{{ {','.join(elements)} }}"
        )

    async def remove_elements(self, elements):
        """Remove a list of elements to the set."""
        if not self.initialized:
            raise RuntimeError(f"Set {self.name} hasn't been loaded.")

        await nft(
                'delete', 'element', self.family, self.table, self.name,
                f"{{ {','.join(elements)} }}"
        )

    def __str__(self):
        if not self.initialized:
            raise RuntimeError(f"Set {self.name} hasn't been loaded.")

        return f"@{self.name}"