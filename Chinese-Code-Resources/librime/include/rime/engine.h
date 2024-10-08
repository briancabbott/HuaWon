//
// Copyleft RIME Developers
// License: GPLv3
//
// 2011-03-14 GONG Chen <chen.sst@gmail.com>
//
#ifndef RIME_ENGINE_H_
#define RIME_ENGINE_H_

#include <string>
#include <rime/common.h>
#include <rime/messenger.h>

namespace rime {

class KeyEvent;
class Schema;
class Context;

class Engine : public Messenger {
 public:
  using CommitSink = signal<void (const std::string& commit_text)>;

  virtual ~Engine();
  virtual bool ProcessKey(const KeyEvent& key_event) { return false; }
  virtual void ApplySchema(Schema* schema) {}
  virtual void CommitText(std::string text) { sink_(text); }

  Schema* schema() const { return schema_.get(); }
  Context* context() const { return context_.get(); }
  CommitSink& sink() { return sink_; }

  Context* active_context() const {
    return active_context_ ? active_context_ : context_.get();
  }
  void set_active_context(Context* context = nullptr) {
    active_context_ = context;
  }

  static Engine* Create();

 protected:
  Engine();

  unique_ptr<Schema> schema_;
  unique_ptr<Context> context_;
  CommitSink sink_;
  Context* active_context_ = nullptr;
};

}  // namespace rime

#endif  // RIME_ENGINE_H_
