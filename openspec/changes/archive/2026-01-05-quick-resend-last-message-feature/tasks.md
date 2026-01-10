## 1. HTML 结构

- [x] 1.1 在 `site/index.html` 的 `.input-container` 内、`<textarea>` 之前添加重发区域 div
- [x] 1.2 添加内容预览元素（使用 class="resend-preview"）
- [x] 1.3 添加重发按钮（使用 class="resend-button"，onclick="handleResend()"）

## 2. JavaScript 状态管理

- [x] 2.1 在 `site/app.js` 顶部添加 `lastSentContent` 变量声明
- [x] 2.2 添加 `loadLastSentContent()` 函数从 localStorage 读取历史内容
- [x] 2.3 添加 `updateLastSentContent(text)` 函数保存到 localStorage
- [x] 2.4 添加 `renderResendArea()` 函数根据状态显示/隐藏重发区域
- [x] 2.5 在 `window.onload` 中调用 `loadLastSentContent()` 和 `renderResendArea()`
- [x] 2.6 添加 `handleResend()` 函数处理重发按钮点击事件
- [x] 2.7 在 `sendRequest()` 和 `sendPlainRequest()` 成功回调中调用 `updateLastSentContent(text)`

## 3. CSS 样式

- [x] 3.1 添加 `.resend-area` 容器样式（flexbox 布局，间距，圆角）
- [x] 3.2 添加 `.resend-preview` 样式（flex-grow，单行显示，省略号截断，灰色文本）
- [x] 3.3 添加 `.resend-button` 样式（复用发送按钮样式，固定宽度）
- [x] 3.4 添加 `.resend-area.hidden` 样式（display: none）
- [x] 3.5 添加响应式媒体查询（小屏幕和横屏适配）

## 4. 测试验证

- [x] 4.1 验证首次加载页面时（无历史）重发区域隐藏
- [x] 4.2 验证发送消息后重发区域显示且内容正确
- [x] 4.3 验证点击重发按钮能正确发送上次内容
- [x] 4.4 验证重发成功后重发区域更新为最新内容
- [x] 4.5 验证重发失败后仍可再次重试
- [x] 4.6 验证页面刷新后重发区域保持上次状态
- [x] 4.7 验证长文本预览正确截断并显示省略号
