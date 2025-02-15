import { Editor } from 'https://esm.sh/@tiptap/core'
import StarterKit from 'https://esm.sh/@tiptap/starter-kit'
import Placeholder from 'https://esm.sh/@tiptap/extension-placeholder'
import { Mark, mergeAttributes, InputRule } from 'https://esm.sh/@tiptap/core'

// 自訂 highlight extension，保留 data-d 並支援 input rule（若有需要）
export const CustomHighlight = Mark.create({
  name: 'customHighlight',

  defaultOptions: {
    HTMLAttributes: {},
  },

  addAttributes() {
    return {
      // 將 data-d 當作 description 處理
      description: {
        default: null,
        parseHTML: element => element.getAttribute('data-d'),
        renderHTML: attributes => {
          return attributes.description ? { 'data-d': attributes.description } : {}
        },
      },
    }
  },

  parseHTML() {
    return [
      {
        tag: 'mark',
        getAttrs: dom => ({
          description: dom.getAttribute('data-d'),
        }),
      },
    ]
  },

  renderHTML({ HTMLAttributes }) {
    return ['mark', mergeAttributes(this.options.HTMLAttributes, HTMLAttributes), 0]
  },

  // 如果需要支援從 ==文字== 自動轉換，可使用下列 input rule
  addInputRules() {
    return [
      new InputRule({
        find: /==(.*?)==/g,
        handler: ({ state, range, match }) => {
          const [fullMatch, text] = match
          const { tr } = state
          // 預設描述內容，若有額外處理請依需求修改
          const highlightMark = this.type.create({ description: '預設描述' })
          tr.replaceWith(range.from, range.to, state.schema.text(text, [highlightMark]))
          return tr
        },
      }),
    ]
  },
})

// 初始化 tiptap 編輯器
export const tiptapEditor = new Editor({
  element: document.querySelector('.tiptap-editor'),
  extensions: [
    StarterKit,
    Placeholder.configure({
      placeholder: '開啟會議記錄...',
    }),
    CustomHighlight
  ],
  editorProps: {
    attributes: {
      class: 'outline-none',
    },
  },
})