#!/usr/bin/env python3

# spin_lock
# read_lock
# write_lock
# mutex_lock
# sem_lock
# prepare_lock
# enable_lock
# rcu_lock
# rcu_read_lock


spin_lock_list = ["spin_lock",
                  "spin_lock_nested",
                  "_spin_lock",
                  "_spin_lock_nested",
                  "__spin_lock",
                  "__spin_lock_nested",
                  "raw_spin_lock",
                  "_raw_spin_lock",
                  "_raw_spin_lock_nested",
                  "__raw_spin_lock",
                  "spin_lock_irq",
                  "_spin_lock_irq",
                  "__spin_lock_irq",
                  "_raw_spin_lock_irq",
                  "spin_lock_irqsave",
                  "_spin_lock_irqsave",
                  "__spin_lock_irqsave",
                  "_raw_spin_lock_irqsave",
                  "__raw_spin_lock_irqsave",
                  "spin_lock_irqsave_nested",
	              "_spin_lock_irqsave_nested",
	              "__spin_lock_irqsave_nested",
	              "_raw_spin_lock_irqsave_nested",
                  "spin_lock_bh",
                  "_spin_lock_bh",
                  "__spin_lock_bh",
                  "spin_trylock",
	              "_spin_trylock",
	              "__spin_trylock",
	              "raw_spin_trylock",
	              "_raw_spin_trylock",
	              "spin_trylock_irq",
	              "spin_trylock_irqsave",
	              "spin_trylock_bh", 
	              "_spin_trylock_bh",
	              "__spin_trylock_bh",
	              "__raw_spin_trylock",
	              "_atomic_dec_and_lock",
                  "lock_sock",
                  "lock_sock_nested",
                  "lock_sock_fast",
                  "__lock_sock",
                  "lock_task_sighand",
                  "ext4_lock_group"]

spin_unlock_list = ["spin_unlock",
                    "_spin_unlock",
                    "__spin_unlock",
                    "raw_spin_unlock",
                    "_raw_spin_unlock",
                    "__raw_spin_unlock",
                    "spin_unlock_irq",
                    "_spin_unlock_irq",
                    "__spin_unlock_irq",
                    "_raw_spin_unlock_irq",
                    "__raw_spin_unlock_irq",
                    "spin_unlock_irqrestore",
                    "_spin_unlock_irqrestore",
                    "__spin_unlock_irqrestore",
                    "_raw_spin_unlock_irqsave",
                    "__raw_spin_unlock_irqsave",
                    "spin_unlock_bh",
                    "_spin_unlock_bh",
                    "__spin_unlock_bh",
                    "release_sock",
                    "__release_sock",
                    "deactivate_locked_super",
                    "ext4_unlock_group"]

read_lock_list = ["read_lock",
	              "down_read",
	              "down_read_nested",
	              "down_read_trylock",
	              "down_read_killable",
	              "_read_lock",
	              "__read_lock",
	              "_raw_read_lock",
	              "__raw_read_lock",
	              "read_lock_irq",
	              "_read_lock_irq",
	              "__read_lock_irq",
	              "_raw_read_lock_irq",
	              "_raw_read_lock_bh",
	              "read_lock_irqsave",
	              "_read_lock_irqsave",
	              "__read_lock_irqsave",
	              "read_lock_bh",
	              "_read_lock_bh",
	              "__read_lock_bh",
	              "__raw_read_lock_bh",
                  "_raw_read_lock_irqsave",
	              "_raw_spin_lock_bh",
	              "_raw_spin_lock_nest_lock",
                  "generic__raw_read_trylock",
	              "read_trylock",
	              "_read_trylock",
	              "raw_read_trylock",
	              "_raw_read_trylock",
	              "__raw_read_trylock",
	              "__read_trylock"]

read_unlock_list = ["up_read",
                    "read_unlock",
                    "_read_unlock",
                    "__read_unlock",
                    "_raw_read_unlock",
                    "__raw_read_unlock",
                    "read_unlock_irq",
                    "_read_unlock_irq",
                    "__read_unlock_irq",
                    "_raw_read_unlock_irq",
                    "_raw_read_unlock_bh",
                    "read_unlock_irqrestore",
                    "_read_unlock_irqrestore",
                    "__read_unlock_irqrestore",
                    "read_unlock_bh",
                    "_read_unlock_bh",
                    "__read_unlock_bh",
                    "__raw_read_unlock_bh",
                    "_raw_read_unlock_irqrestore",
                    "_raw_spin_unlock_bh"]

write_lock_list = ["write_lock",
                   "_raw_write_lock_irqsave",
                   "down_write",
                   "down_write_nested",
                   "_write_lock",
                   "__write_lock",
                   "write_lock_irq",
                   "_write_lock_irq",
                   "__write_lock_irq",
                   "write_lock_irqsave",
                   "_write_lock_irqsave",
                   "__write_lock_irqsave",
                   "write_lock_bh",
                   "_write_lock_bh",
                   "__write_lock_bh",
                   "_raw_write_lock",
                   "__raw_write_lock",
                   "_raw_write_lock_bh",
                   "_raw_write_lock_irq",
                   "write_trylock",
                   "_write_trylock",
                   "raw_write_trylock",
                   "_raw_write_trylock",
                   "__write_trylock",
                   "__raw_write_trylock",
                   "down_write_trylock",
                   "down_write_killable",
                   "rw_lock"]

write_unlock_list = ["write_unlock",
                     "_raw_write_unlock_irqrestore",
                     "__raw_write_unlock_irq",
                     "__raw_write_unlock_irqrestore",
                     "up_write",
                     "_write_unlock",
                     "__write_unlock",
                     "write_unlock_irq",
                     "_write_unlock_irq",
                     "__write_unlock_irq",
                     "_raw_write_unlock_irq",
                     "write_unlock_irqrestore",
                     "_write_unlock_irqrestore",
                     "__write_unlock_irqrestore",
                     "write_unlock_bh",
                     "_write_unlock_bh",
                     "__write_unlock_bh",
                     "_raw_write_unlock",
                     "__raw_write_unlock",
                     "_raw_write_unlock_bh",
                     "rw_unlock"]

mutex_lock_list = ["mutex_lock",
                   "mutex_lock_nested",
                   "mutex_lock_io",
                   "mutex_lock_io_nested",
                   "mutex_lock_interruptible",
                   "mutex_lock_interruptible_nested",
                   "mutex_lock_killable",
                   "mutex_lock_killable_nested",
                   "mutex_trylock",
                   "ww_mutex_lock",
                   "__ww_mutex_lock",
                   "ww_mutex_lock_interruptible",
                   "ffs_mutex_lock",
                   "dma_resv_lock",
                   "dma_resv_trylock",
                   "dma_resv_lock_interruptible",
                   "modeset_lock",
                   "drm_ modeset_lock",
                   "drm_modeset_lock_single_interruptible",
                   "i915_gem_object_lock_interruptible",
                   "i915_gem_object_lock",
                   "msm_gem_lock",
                   "reiserfs_write_lock_nested",
                   "sem_lock"]

mutex_unlock_list = ["mutex_unlock",
                     "ww_mutex_unlock",
                     "dma_resv_unlock",
                     "modeset_unlock",
                     "reiserfs_write_unlock_nested",
                     "sem_unlock"]

sem_lock_list = ["down",
                 "down_trylock",
                 "down_timeout",
                 "down_interruptible",
                 "down_killable",
                 "gfs2_trans_begin"]

sem_unlock_list = ["up"]

prepare_lock_list = ["clk_prepare_lock"]

prepare_unlock_list = ["clk_prepare_unlock"]

enable_lock_list = ["clk_enable_lock"]

enable_unlock_list = ["clk_enable_unlock"]

rcu_lock_list = ["rcu_lock_acquire"]

rcu_unlock_list = ["rcu_lock_release"]

rcu_read_lock_list = ["rcu_read_lock",
                      "rcu_read_lock_bh",
                      "rcu_read_lock_sched",
                      "rcu_read_lock_sched_notrace"]

rcu_read_unlock_list = ["rcu_read_unlock",
                        "rcu_read_unlock_bh",
                        "rcu_read_unlock_sched",
                        "rcu_read_unlock_sched_notrace"]

all_lock_list = [spin_lock_list, read_lock_list, write_lock_list, mutex_lock_list, sem_lock_list, prepare_lock_list, enable_lock_list, rcu_lock_list, rcu_read_lock_list]
all_unlock_list = [spin_unlock_list, read_unlock_list, write_unlock_list, mutex_unlock_list, sem_unlock_list, prepare_unlock_list, enable_unlock_list, rcu_unlock_list, rcu_read_unlock_list]

